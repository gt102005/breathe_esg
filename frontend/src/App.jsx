import { useEffect, useState } from 'react';
import { ingestFile, fetchRecords, reviewRecord } from './api';

const ingestDefinitions = [
  { key: 'sap', label: 'SAP Fuel + Procurement', description: 'Upload a CSV export from SAP containing material, quantity and date fields.' },
  { key: 'utility', label: 'Utility Electricity', description: 'Upload a facility electricity CSV containing billing periods, consumption and meter IDs.' },
  { key: 'travel', label: 'Corporate Travel', description: 'Upload a JSON export with flights, hotels, and ground transport trips.' },
];

function App() {
  const [selectedSource, setSelectedSource] = useState('sap');
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRecords();
  }, []);

  const loadRecords = async () => {
    setLoading(true);
    try {
      const response = await fetchRecords();
      setRecords(response.data?.results || []);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) {
      setMessage('Please choose a file first.');
      return;
    }
    setMessage('Uploading...');
    try {
      const result = await ingestFile(selectedSource, file);
      setMessage(`Created ${result.data.created} rows. ${result.data.errors.length} errors.`);
      setFile(null);
      loadRecords();
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Upload failed.');
    }
  };

  const handleReview = async (id, status) => {
    const comment = window.prompt('Review comment (optional)');
    await reviewRecord(id, { status, review_comments: comment || '', reviewed_by: 'analyst@example.com' });
    loadRecords();
  };

  const summary = records.reduce(
    (acc, record) => {
      acc.total += 1;
      if (record.status === 'approved') acc.approved += 1;
      if (record.status === 'failed') acc.failed += 1;
      if (record.status === 'pending') acc.pending += 1;
      return acc;
    },
    { total: 0, approved: 0, failed: 0, pending: 0 }
  );

  return (
    <div className="app-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">Breathe ESG</p>
          <h1>Data ingestion & review</h1>
          <p className="lead">Upload SAP, utility, and travel data, then review normalized emissions before audit submission.</p>
        </div>
        <div className="badge">Prototype</div>
      </header>

      <section className="workspace-grid">
        <aside className="ingest-panel card">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Source ingestion</p>
              <h2>Upload data</h2>
            </div>
            <span className="small-tag">Live demo</span>
          </div>

          <div className="source-tabs">
            {ingestDefinitions.map((source) => (
              <button
                key={source.key}
                className={selectedSource === source.key ? 'active' : 'tab-button'}
                onClick={() => setSelectedSource(source.key)}
                type="button"
              >
                {source.label}
              </button>
            ))}
          </div>

          <p className="hint">{ingestDefinitions.find((item) => item.key === selectedSource).description}</p>

          <form className="upload-form" onSubmit={handleUpload}>
            <label className="file-input">
              <span>{file ? file.name : 'Choose a file...'}</span>
              <input type="file" onChange={(event) => setFile(event.target.files[0])} />
            </label>
            <button className="primary-button" type="submit">Upload</button>
          </form>

          {message && <div className="message">{message}</div>}
        </aside>

        <section className="summary-panel card">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Review snapshot</p>
              <h2>Queue summary</h2>
            </div>
          </div>

          <div className="summary-grid">
            <div className="summary-card">
              <span>Total rows</span>
              <strong>{summary.total}</strong>
            </div>
            <div className="summary-card">
              <span>Pending review</span>
              <strong>{summary.pending}</strong>
            </div>
            <div className="summary-card">
              <span>Approved</span>
              <strong>{summary.approved}</strong>
            </div>
            <div className="summary-card">
              <span>Rejected</span>
              <strong>{summary.failed}</strong>
            </div>
          </div>
        </section>
      </section>

      <section className="dashboard card">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Review queue</p>
            <h2>Emissions records</h2>
          </div>
          <button className="secondary-button" type="button" onClick={loadRecords}>Refresh</button>
        </div>

        {loading ? (
          <div className="loading-state">Loading records…</div>
        ) : records.length === 0 ? (
          <div className="empty-state">
            <h3>No records yet</h3>
            <p>Upload a source file to populate the review queue.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Category</th>
                  <th>Scope</th>
                  <th>Activity</th>
                  <th>Period</th>
                  <th>Quantity</th>
                  <th>Emissions</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.id}>
                    <td>{record.id}</td>
                    <td>{record.category}</td>
                    <td>{record.scope}</td>
                    <td>{record.activity_type}</td>
                    <td>{record.period_start || record.activity_date || '-'} / {record.period_end || '-'}</td>
                    <td>{record.activity_quantity ?? '-'} {record.activity_unit}</td>
                    <td>{record.emission_kg_co2e ?? '-'} kgCO2e</td>
                    <td><span className={`status-pill ${record.status}`}>{record.status}</span></td>
                    <td className="action-buttons">
                      <button className="approve" onClick={() => handleReview(record.id, 'approved')} disabled={record.status === 'approved'}>Approve</button>
                      <button className="reject" onClick={() => handleReview(record.id, 'failed')} disabled={record.status === 'failed'}>Reject</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;
