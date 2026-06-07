import { useState, useEffect } from 'react';
import { Search, Sparkles, AlertCircle, Share2, Check } from 'lucide-react';

const BACKEND_URL =
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8080'
    : window.location.origin;

const LOADING_STEPS = [
  'Scraping public GitHub profile...',
  'Analyzing repository languages and stargazers...',
  'Invoking Gemini to determine your developer vibe...',
  'Selecting card theme and calculating statistics...',
  'Generating beautiful custom card HTML...',
  'Finalizing and saving your developer card...'
];

function App() {
  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState(null);
  const [cardHtml, setCardHtml] = useState(null);
  const [cardTheme, setCardTheme] = useState('builder');
  const [shareUrl, setShareUrl] = useState(null);
  const [copied, setCopied] = useState(false);

  // Rotate loading text steps when generating
  useEffect(() => {
    let interval;
    if (loading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < LOADING_STEPS.length - 1 ? prev + 1 : prev));
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const extractUsername = (raw) => {
    let username = raw.trim();
    if (!username) return '';

    // Auto-extract username from a GitHub URL if they paste one
    if (username.includes('github.com')) {
      try {
        const parts = username.split('github.com/');
        if (parts.length > 1) {
          username = parts[1].split('/')[0].split('?')[0].split('#')[0];
        }
      } catch (e) {
        // ignore
      }
    } else if (username.includes('http://') || username.includes('https://')) {
      try {
        const urlObj = new URL(username);
        const pathname = urlObj.pathname.replace(/^\/|\/$/g, '');
        username = pathname.split('/')[0];
      } catch (e) {
        // ignore
      }
    }

    return username.replace('@', '');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      generateCard();
    }
  };

  const generateCard = async () => {
    const usernameInput = extractUsername(inputVal);

    if (!usernameInput) {
      setError('Please enter a GitHub username.');
      return;
    }

    // Validate the username character format (alphanumeric and hyphens only)
    const usernameRegex = /^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$/;
    if (!usernameRegex.test(usernameInput)) {
      setError('Please enter a valid GitHub username (letters, numbers, and single hyphens only).');
      return;
    }

    // Reset state
    setLoading(true);
    setError(null);
    setCardHtml(null);
    setShareUrl(null);

    try {
      const url = `${BACKEND_URL}/generate`;
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameInput })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate card');
      }

      if (data.html) {
        // Detect theme from the HTML for background glow
        let theme = 'builder';
        if (data.html.includes('open-source-hero')) theme = 'open-source-hero';
        else if (data.html.includes('researcher')) theme = 'researcher';
        else if (data.html.includes('hacker')) theme = 'hacker';
        else if (data.html.includes('designer')) theme = 'designer';
        
        setCardTheme(theme);
        setCardHtml(data.html);
        
        // Formulate correct sharing URL
        const baseShare = BACKEND_URL.endsWith('/') ? BACKEND_URL.slice(0, -1) : BACKEND_URL;
        setShareUrl(`${baseShare}${data.url}`);
      } else {
        throw new Error('No card content generated. Please try again.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyUrl = () => {
    if (shareUrl) {
      navigator.clipboard.writeText(shareUrl).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  return (
    <div className="container">
      <h1 className="title">GitHub Dev Card</h1>
      <div className="subheading">Enter any public GitHub username to reveal their developer vibe.</div>

      <div className="search-box-wrapper">
        <div className="search-icon">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
          </svg>
        </div>
        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter username or paste profile link..."
          disabled={loading}
        />
        <button onClick={generateCard} disabled={loading}>
          {loading ? (
            'Analyzing...'
          ) : (
            <>
              Generate <Sparkles size={16} />
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="error-container">
          <AlertCircle className="error-icon" size={20} />
          <div>{error}</div>
        </div>
      )}

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">{LOADING_STEPS[loadingStep]}</div>
          
          {/* Skeleton card loader */}
          <div className="skeleton-card">
            <div className="skeleton-shimmer"></div>
            <div className="skeleton-header">
              <div className="skeleton-avatar"></div>
              <div className="skeleton-title-box">
                <div className="skeleton-line short"></div>
                <div className="skeleton-line medium"></div>
              </div>
            </div>
            <div className="skeleton-line long"></div>
            <div className="skeleton-line long"></div>
            <div className="skeleton-pills">
              <div className="skeleton-pill"></div>
              <div className="skeleton-pill"></div>
              <div className="skeleton-pill"></div>
            </div>
            <div className="skeleton-stats">
              <div className="skeleton-stat"></div>
              <div className="skeleton-stat"></div>
            </div>
            <div className="skeleton-line medium" style={{ marginTop: '10px' }}></div>
          </div>
        </div>
      )}

      {cardHtml && !loading && (
        <div className="result-container">
          <div className={`card-glow ${cardTheme}`}></div>
          <div className="card-wrapper-inner">
            <div className="share-action-bar">
              <button className={`share-btn ${copied ? 'copied' : ''}`} onClick={copyUrl}>
                {copied ? (
                  <>
                    <Check size={16} /> Copied Link!
                  </>
                ) : (
                  <>
                    <Share2 size={16} /> Share Card
                  </>
                )}
              </button>
            </div>
            <div dangerouslySetInnerHTML={{ __html: cardHtml }} />
          </div>
        </div>
      )}

      <footer>
        <p>
          GitHub Dev Card &copy; {new Date().getFullYear()}
        </p>
      </footer>
    </div>
  );
}

export default App;
