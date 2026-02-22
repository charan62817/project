import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import axios from 'axios';
import { Leaf } from 'lucide-react';

const API_URL = 'http://localhost:8002';

// Helper to get color based on compatibility level
const getColorForLevel = (level) => {
  if (level.includes("Excellent")) return "#00ff88"; // Green
  if (level.includes("Very Good")) return "#90ee90"; // Light Green
  if (level.includes("Good")) return "#ffcc00"; // Yellow
  if (level.includes("Moderate")) return "#ff9900"; // Orange
  if (level.includes("Low")) return "#ff2e63"; // Red
  return "#b3b3b3"; // Default grey
};

// Custom Styles for React Select to match Glassmorphism
const selectStyles = {
  control: (base) => ({
    ...base,
    background: 'rgba(0,0,0,0.2)',
    borderColor: 'rgba(255,255,255,0.2)',
    borderRadius: '8px',
    padding: '5px',
    color: 'white',
    boxShadow: 'none',
    '&:hover': { borderColor: 'rgba(255,255,255,0.4)' }
  }),
  menu: (base) => ({
    ...base,
    background: '#1a1a2e',
    border: '1px solid rgba(255,255,255,0.1)',
    zIndex: 9999,
    position: 'absolute'
  }),
  menuPortal: (base) => ({
    ...base,
    zIndex: 9999
  }),
  option: (base, state) => ({
    ...base,
    background: state.isFocused ? '#302b63' : 'transparent',
    color: 'white',
    cursor: 'pointer'
  }),
  singleValue: (base) => ({ ...base, color: 'white' }),
  input: (base) => ({ ...base, color: 'white' }),
  placeholder: (base) => ({ ...base, color: '#b3b3b3' }),
};

const labelStyle = {
  display: 'block',
  marginBottom: '8px',
  fontSize: '0.9rem',
  color: '#b3b3b3'
};

const inputStyle = {
  width: '100%',
  padding: '12px',
  borderRadius: '8px',
  border: '1px solid rgba(255,255,255,0.2)',
  background: 'rgba(0,0,0,0.2)',
  color: 'white',
  fontSize: '1rem',
  transition: 'border-color 0.3s'
};

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

const FoodCompatibility = ({ activeTab }) => {
  const [foodOptions, setFoodOptions] = useState([]);

  // Disease options for the select dropdown
  const diseaseOptions = [
    { value: 'none', label: 'None' },
    { value: 'diabetes', label: 'Diabetes' },
    { value: 'hypertension', label: 'Hypertension / High Blood Pressure' },
    { value: 'anemia', label: 'Anemia' },
    { value: 'cholesterol', label: 'High Cholesterol' },
    { value: 'digestion', label: 'Digestive Issues' },
    { value: 'heart', label: 'Heart Disease' },
    { value: 'obesity', label: 'Obesity' },
    { value: 'thyroid', label: 'Thyroid Issues' },
    { value: 'arthritis', label: 'Arthritis' },
    { value: 'asthma', label: 'Asthma' },
    { value: 'allergies', label: 'Allergies' }
  ];

  // Form State
  const [selectedFood1, setSelectedFood1] = useState(null);
  const [selectedFood2, setSelectedFood2] = useState(null);
  const [contextData, setContextData] = useState({
    age: '30',
    season: 'summer',
    time: 'day',
    disease: 'none'
  });

  const [result, setResult] = useState(null);
  const [suggestions, setSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch Food List on Mount
  useEffect(() => {
    axios.get(`${API_URL}/foods`)
      .then(res => {
        const transformedOptions = res.data.map(food => ({
          value: food.id,
          label: food.name,
          category: food.category
        }));
        setFoodOptions(transformedOptions);
      })
      .catch(err => console.error("Backend not running?", err));
  }, []);

  // Clear results when tab changes
  useEffect(() => {
    setResult(null);
    setSuggestions(null);
    setSelectedFood1(null);
    setSelectedFood2(null);
    setContextData({
      age: '30',
      season: 'summer',
      time: 'day',
      disease: 'none'
    });
  }, [activeTab]);

  const handleContextChange = (e) => {
    setContextData({
      ...contextData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setSuggestions(null);

    try {
      if (activeTab === 'check') {
        if (!selectedFood1 || !selectedFood2) {
          setLoading(false);
          alert("Please select both food items.");
          return;
        }

        const payload = {
          food1_id: selectedFood1.value,
          food2_id: selectedFood2.value,
          age: parseInt(contextData.age) || 30,
          season: contextData.season,
          time: contextData.time
        };

        const res = await axios.post(`${API_URL}/predict_compatibility`, payload);
        setResult(res.data);

      } else if (activeTab === 'suggest') {
        const payload = {
          age: parseInt(contextData.age) || 30,
          season: contextData.season,
          time: contextData.time,
          disease: contextData.disease || 'none'
        };

        const res = await axios.post(`${API_URL}/suggest_foods`, payload);
        setSuggestions(res.data);
      }
    } catch (error) {
      console.error(error);
      alert("Error connecting to the AI Backend. Make sure backend.py is running!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="glass-panel fade-in" style={{ animationDelay: '0.2s' }}>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ gridColumn: 'span 2' }}>
          <h2 style={{ marginBottom: '15px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px' }}>
            {activeTab === 'check' ? 'Select Foods to Compare' : 'Enter Health Profile'}
          </h2>
        </div>

        {activeTab === 'check' && (
          <>
            <div className="input-group">
              <label style={labelStyle}>First Food Item</label>
              <Select
                options={foodOptions}
                value={selectedFood1}
                onChange={setSelectedFood1}
                styles={selectStyles}
                placeholder={foodOptions.length > 0 ? "Search food..." : "Loading foods..."}
                menuPortalTarget={document.body}
                isDisabled={foodOptions.length === 0}
              />
            </div>

            <div className="input-group">
              <label style={labelStyle}>Second Food Item</label>
              <Select
                options={foodOptions}
                value={selectedFood2}
                onChange={setSelectedFood2}
                styles={selectStyles}
                placeholder={foodOptions.length > 0 ? "Search food..." : "Loading foods..."}
                menuPortalTarget={document.body}
                isDisabled={foodOptions.length === 0}
              />
            </div>
          </>
        )}

        {/* Context Inputs */}
        <div className="input-group">
          <label style={labelStyle}>Your Age</label>
          <input
            type="number"
            name="age"
            placeholder="30"
            value={contextData.age}
            onChange={handleContextChange}
            style={inputStyle}
          />
        </div>

        <div className="input-group">
          <label style={labelStyle}>Season</label>
          <select name="season" value={contextData.season} onChange={handleContextChange} style={inputStyle}>
            <option value="summer">Summer</option>
            <option value="winter">Winter</option>
            <option value="rainy">Rainy / Monsoon</option>
          </select>
        </div>

        <div className="input-group">
          <label style={labelStyle}>Time of Intake</label>
          <select name="time" value={contextData.time} onChange={handleContextChange} style={inputStyle}>
            <option value="day">Morning / Day</option>
            <option value="night">Evening / Night</option>
          </select>
        </div>

        {activeTab === 'suggest' && (
          <div className="input-group">
            <label style={labelStyle}>Medical Conditions</label>
            <Select
              options={diseaseOptions}
              value={diseaseOptions.find(option => option.value === contextData.disease)}
              onChange={(selected) => {
                setContextData({
                  ...contextData,
                  disease: selected ? selected.value : 'none'
                });
              }}
              styles={selectStyles}
              placeholder="Select medical condition..."
              menuPortalTarget={document.body}
            />
          </div>
        )}

        <div style={{ gridColumn: 'span 2', marginTop: '20px' }}>
          <button
            type="submit"
            style={activeTab === 'check' ? buttonStyle : { ...buttonStyle, background: 'linear-gradient(to right, #11998e, #38ef7d)' }}
            onMouseOver={(e) => e.target.style.transform = 'scale(1.02)'}
            onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
          >
            {loading ? (activeTab === 'check' ? 'Processing with AI...' : 'Generating Suggestions...') : (activeTab === 'check' ? 'Analyze Compatibility' : 'Generate Suggestions')}
          </button>
        </div>
      </form>

      {/* Results Section - Compatibility */}
      {activeTab === 'check' && result && (
        <section style={{ marginTop: '30px', animationDelay: '0.1s', borderLeft: `6px solid ${getColorForLevel(result.level)}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '1.8rem', color: getColorForLevel(result.level) }}>
              {result.level}
            </h2>
            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '5px 15px', borderRadius: '20px', fontSize: '0.9rem' }}>
              AI Score: {result.score}/10
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div style={{ background: 'rgba(0,255,136,0.05)', padding: '15px', borderRadius: '8px', border: '1px solid rgba(0,255,136,0.1)' }}>
              <h3 style={{ color: '#00ff88', marginBottom: '10px' }}>Why Eat?</h3>
              {result.pros.length > 0 ? (
                <ul style={{ paddingLeft: '20px' }}>
                  {result.pros.map((p, i) => <li key={i} style={{ marginBottom: '5px' }}>{p}</li>)}
                </ul>
              ) : (
                <p style={{ opacity: 0.7, fontStyle: 'italic' }}>No strong synergy found.</p>
              )}
            </div>

            <div style={{ background: 'rgba(255,46,99,0.05)', padding: '15px', borderRadius: '8px', border: '1px solid rgba(255,46,99,0.1)' }}>
              <h3 style={{ color: '#ff2e63', marginBottom: '10px' }}>Why Avoid?</h3>
              {result.cons.length > 0 ? (
                <ul style={{ paddingLeft: '20px' }}>
                  {result.cons.map((c, i) => <li key={i} style={{ marginBottom: '5px' }}>{c}</li>)}
                </ul>
              ) : (
                <p style={{ opacity: 0.7, fontStyle: 'italic' }}>No major conflict.</p>
              )}
            </div>
          </div>
        </section>
      )}

      {/* AI Suggestions Results */}
      {activeTab === 'suggest' && suggestions && (
        <section style={{ marginTop: '30px', animationDelay: '0.1s', borderLeft: '6px solid #00ff88' }}>
          <h2 style={{ fontSize: '1.8rem', color: '#00ff88', marginBottom: '10px' }}>
            AI Recommended Foods
          </h2>
          <p style={{ opacity: 0.9, marginBottom: '20px', fontSize: '1.1rem' }}>
            {suggestions.reason}
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '15px' }}>
            {suggestions.suggestions.map((item, index) => (
              <div key={index} style={{
                background: 'rgba(255,255,255,0.1)',
                padding: '15px',
                borderRadius: '12px',
                textAlign: 'center',
                border: '1px solid rgba(255,255,255,0.2)'
              }}>
                <span style={{ fontSize: '1.1rem', fontWeight: '500' }}>{item}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
};

export default FoodCompatibility;