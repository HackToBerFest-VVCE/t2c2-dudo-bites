:root {
  font-family: Inter, system-ui, sans-serif;
  color: #e5e7eb;
  background: #0f172a;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
}

.app-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.status-pill {
  background: #1d4ed8;
  color: white;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 0.9rem;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.card {
  background: #111827;
  border: 1px solid #1f2937;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.28);
}

.summary-card {
  grid-column: span 2;
}

.score {
  font-size: 3rem;
  font-weight: 700;
  margin: 12px 0;
}

ul {
  padding-left: 18px;
  margin: 12px 0 0;
}

li {
  margin-bottom: 10px;
}
