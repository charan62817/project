import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ScanLine } from 'lucide-react';

const API_URL = 'http://localhost:8002'; // Backend API URL

const PrescriptionScanner = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [scanLoading, setScanLoading] = useState(false);

  // Clear results when tab changes (handled by parent now, but good to keep local state)
  useEffect(() => {
    setFile(null);
    setPreview(null);
    setScanResult(null);
  }, []); // Only run once on mount for initial clear, parent handles tab changes

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setScanResult(null); // Clear previous results
    }
  };

  const scanPrescription = async () => {
    if (!file) {
      alert("Please upload a prescription image first");
      return;
    }

    setScanLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await axios.post(`${API_URL}/scan`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setScanResult(response.data);
    } catch (error) {
      console.error("Scan failed:", error);
      alert("Failed to scan prescription. Please try again.");
    } finally {
      setScanLoading(false);
    }
  };

  const resetScanner = () => {
    setFile(null);
    setPreview(null);
    setScanResult(null);
    setScanLoading(false);
  };

  return (
    <main className="glass-panel fade-in" style={{ animationDelay: '0.2s' }}>
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h2 style={{ marginBottom: '15px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px' }}>
          🏥 Prescription Scanner
        </h2>
        <p style={{ opacity: 0.8 }}>Upload a prescription image to extract medicine information</p>
      </div>

      <div className="upload-section">
        <div className="upload-area">
          <input
            type="file"
            id="file-input"
            accept="image/*"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-input" className="upload-button">
            📷 Choose Prescription Image
          </label>

          {file && (
            <div className="file-info">
              <p>📄 {file.name}</p>
              <button onClick={resetScanner} className="reset-button">❌ Remove</button>
            </div>
          )}
        </div>

        {preview && (
          <div className="preview-section">
            <h3>📋 Image Preview</h3>
            <img src={preview} alt="Prescription preview" className="preview-image" />
          </div>
        )}
      </div>

      <div className="action-section">
        <button
          onClick={scanPrescription}
          disabled={!file || scanLoading}
          className={`scan-button ${scanLoading ? 'loading' : ''}`}
          style={{ ...buttonStyle, background: 'linear-gradient(to right, #ff8800, #ff2e63)' }} // Custom style for scan button
          onMouseOver={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
        >
          {scanLoading ? (
            <>
              🔍 Scanning Prescription...
              <div className="spinner"></div>
            </>
          ) : (
            '🔍 Scan Prescription'
          )}
        </button>
      </div>

      {scanResult && (
        <div className="results-section">
          {scanResult.success ? (
            <>
              <div className="extracted-text">
                <h3>📝 Extracted Text</h3>
                <div className="text-content">
                  <pre>{scanResult.extracted_text || "No text could be extracted from the image."}</pre>
                </div>
              </div>

              {scanResult.medicines && scanResult.medicines.length > 0 ? (
                <div className="medicines-section">
                  <h3>💊 Medicines Found ({scanResult.medicines_found})</h3>
                  <div className="medicines-grid">
                    {scanResult.medicines.map((med, index) => (
                      <div key={index} className="medicine-card">
                        <div className="medicine-header">
                          <h4>{med.medicine}</h4>
                        </div>
                        <div className="medicine-info">
                          <div className="info-item">
                            <strong>💡 Use:</strong>
                            <p>{med.use}</p>
                          </div>
                          <div className="info-item">
                            <strong>📋 How to take:</strong>
                            <p>{med.how_to_take}</p>
                          </div>
                          <div className="info-item">
                            <strong>⚠️ Side effects:</strong>
                            <p>{Array.isArray(med.side_effects) ? med.side_effects.join(", ") : med.side_effects}</p>
                          </div>
                          <div className="info-item warning">
                            <strong>🚨 Warning:</strong>
                            <p>{med.warning}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="no-medicines">
                  <h3>❌ No Recognized Medicines Found</h3>
                  <p>The scanner couldn't identify any medicines in the image. This could be due to:</p>
                  <ul>
                    <li>Image quality or clarity</li>
                    <li>Handwriting that's hard to read</li>
                    <li>Medicines not in our database</li>
                  </ul>
                  <p>Try uploading a clearer image or consult a pharmacist.</p>
                </div>
              )}
            </>
          ) : (
            <div className="error-section">
              <h3>❌ Scan Failed</h3>
              <p>{scanResult.error || "An unknown error occurred"}</p>
              <button onClick={scanPrescription} className="retry-button">
                🔄 Try Again
              </button>
            </div>
          )}

          <div className="disclaimer-section">
            <div className="disclaimer-box">
              <h4>⚠️ IMPORTANT MEDICAL DISCLAIMER</h4>
              <p className="disclaimer-text">
                {scanResult.disclaimer || "This information is for educational purposes only and is not a substitute for professional medical advice. Always consult your healthcare provider before starting, stopping, or changing any medication. The analysis is based on common medicine names and may not be 100% accurate."}
              </p>
              <p className="disclaimer-note">
                {scanResult.note || "This app provides general information about common medications. It does not provide medical advice, diagnosis, or treatment recommendations."}
              </p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};

// Placeholder buttonStyle - will be passed from App.jsx or defined globally if needed
const buttonStyle = {
  width: '100%',
  padding: '15px',
  borderRadius: '8px',
  background: 'linear-gradient(to right, #00c6ff, #0072ff)',
  border: 'none',
  color: 'white',
  fontSize: '1.1rem',
  fontWeight: 'bold',
  cursor: 'pointer',
  transition: 'transform 0.2s, box-shadow 0.2s',
  boxShadow: '0 4px 15px rgba(0, 114, 255, 0.3)'
};

export default PrescriptionScanner;