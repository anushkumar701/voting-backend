// Central API base URL config
// In development:  proxied via package.json "proxy" → http://localhost:5000
// In production:   set REACT_APP_API_URL to your Railway backend URL

const API_BASE = process.env.REACT_APP_API_URL || '';

export default API_BASE;
