import React, { useState } from 'react';

export default function App() {
  const [city, setCity] = useState('');
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getCoordinates = async (cityName) => {
    const geoUrl = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(cityName)}&count=1&language=en&format=json`;
    const res = await fetch(geoUrl);
    if (!res.ok) throw new Error('Failed to fetch location');
    const data = await res.json();
    if (!data.results || data.results.length === 0) throw new Error('City not found');
    return data.results[0];
  };

  const getWeather = async (lat, lon) => {
    const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`;
    const res = await fetch(weatherUrl);
    if (!res.ok) throw new Error('Failed to fetch weather');
    const data = await res.json();
    return data.current_weather;
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setWeather(null);

    try {
      const location = await getCoordinates(city);
      const weatherData = await getWeather(location.latitude, location.longitude);
      setWeather({ ...weatherData, name: location.name, country: location.country });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGeolocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation not supported');
      return;
    }

    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          const weatherData = await getWeather(lat, lon);
          setWeather({ ...weatherData, name: 'Your Location', country: '' });
        } catch (err) {
          setError('Failed to fetch local weather');
        } finally {
          setLoading(false);
        }
      },
      (err) => {
        setError('Permission denied or location unavailable');
        setLoading(false);
      }
    );
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-400 to-blue-700 text-white font-sans p-4">
      <h1 className="text-3xl font-bold mb-4">Weather Now</h1>
      <form onSubmit={handleSearch} className="flex gap-2 mb-4 w-full max-w-md">
        <input
          type="text"
          placeholder="Enter city name..."
          value={city}
          onChange={(e) => setCity(e.target.value)}
          className="flex-grow p-2 rounded text-black"
          required
        />
        <button type="submit" className="bg-yellow-400 hover:bg-yellow-500 text-black px-4 py-2 rounded">
          Search
        </button>
      </form>
      <button
        onClick={handleGeolocation}
        className="bg-white text-blue-700 px-4 py-2 rounded mb-4 hover:bg-gray-100"
      >
        Use My Location
      </button>

      {loading && <p className="text-lg">Loading...</p>}
      {error && <p className="text-red-200 mt-2">Error: {error}</p>}

      {weather && (
        <div className="bg-white text-blue-800 rounded-lg shadow-md p-6 w-full max-w-sm mt-4">
          <h2 className="text-2xl font-semibold mb-2">{weather.name} {weather.country && `(${weather.country})`}</h2>
          <p className="text-lg mb-1">Temperature: {weather.temperature}°C</p>
          <p className="text-lg mb-1">Wind Speed: {weather.windspeed} km/h</p>
          <p className="text-lg mb-1">Direction: {weather.winddirection}°</p>
          <p className="text-sm text-gray-500 mt-2">Last Updated: {new Date().toLocaleString()}</p>
        </div>
      )}

      <footer className="text-xs text-white mt-8 opacity-80">
        Data from <a href="https://open-meteo.com/" className="underline">Open-Meteo API</a>
      </footer>
    </div>
  );
}
