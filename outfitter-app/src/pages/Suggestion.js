import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';
import './Suggestion.css';
import Navigation from '../components/Navigation';
import checkbox from '../assets/checkbox.svg';

function Suggestion() {
  const [temperature, setTemperature] = useState(null);
  const [weather, setWeather] = useState(null);
  const [suggestedItems, setSuggestedItems] = useState([]);
  const [reasoning, setReasoning] = useState('');
  const [isWorn, setIsWorn] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch smart outfit suggestion
    fetch('/api/suggest-outfit')
      .then(res => res.json())
      .then(data => {
        console.log('Suggestion data:', data);

        // Convert items to include full image paths
        const itemsWithImages = data.items.map(item => {
          let imageSrc;

          // Check if it's a base64 uploaded image
          if (item.image && item.image.startsWith('data:')) {
            imageSrc = item.image;
          } else {
            // It's a regular asset image
            try {
              imageSrc = require(`../assets/clothing/${item.src.substring(2)}`);
            } catch (err) {
              imageSrc = item.src;
            }
          }

          return {
            id: item.id,
            label: item.label,
            src: imageSrc,
            alt: item.alt
          };
        });

        setSuggestedItems(itemsWithImages);
        setTemperature(data.temperature);
        setWeather(data.weather);
        setReasoning(data.reasoning);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching outfit suggestion:', error);
        setLoading(false);
      });
  }, []);

  // Helper function to get image source
  const getImageSrc = (item) => {
    // If the item has a base64 image, use it
    if (item.image && item.image.startsWith('data:')) {
      return item.image;
    }

    // Otherwise try to load from assets
    try {
      return require(`../assets/clothing/${item.src.substring(2)}`);
    } catch (err) {
      return item.src;
    }
  };

  const handleWearClick = () => {
    const item_ids = suggestedItems.map(item => item.id);

    fetch('/api/wear-items', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ item_ids }),
    })
    .then(res => res.json())
    .then(data => {
      console.log(data.message);
      setIsWorn(true);
      setTimeout(() => {
        navigate('/closet');
      }, 300);
    })
    .catch(error => {
      console.error('Error updating worn items:', error);
    });
  };

  if (loading) {
    return (
      <div className="App">
        <h1 className="suggestion-header">Today's Suggestion</h1>
        <div className="divider"></div>
        <div className="based-on">Loading your perfect outfit...</div>
        <Navigation />
      </div>
    );
  }

  return (
    <div className="App">
      <h1 className="suggestion-header">Today's Suggestion</h1>
      <div className="divider"></div>
      <div className="based-on">
        {reasoning}
        {temperature && ` • ${temperature}° F`}
      </div>

      {suggestedItems.length > 0 ? (
        <>
          <div className="suggestion-grid">
            {suggestedItems.map(item => (
              <div key={item.id} className="suggestion-item">
                <img src={item.src} alt={item.alt} />
                <div className="suggestion-item-label">{item.label}</div>
              </div>
            ))}
          </div>
          <div className="suggestion-buttons">
            <button
              className={`suggestion-wear-button ${isWorn ? 'worn' : ''}`}
              onClick={handleWearClick}
              disabled={isWorn}
            >
              {isWorn ? (
                <>
                  <img src={checkbox} alt="checkbox" className="checkbox-icon" />
                  Outfit Confirmed!
                </>
              ) : (
                'Wear'
              )}
            </button>
          </div>
        </>
      ) : (
        <div className="based-on">
          No suitable items found. Try adding more clothes to your closet!
        </div>
      )}

      <Navigation />
    </div>
  );
}

export default Suggestion;