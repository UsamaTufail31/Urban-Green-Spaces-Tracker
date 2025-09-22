# Interactive Leaflet.js Map with Green Spaces

## Features

### 🗺️ Interactive Map
- **Full-width responsive design** that adapts to all screen sizes
- **Mapbox tile integration** (currently using OpenStreetMap as fallback)
- **Smooth navigation** with zoom and pan controls
- **Mobile-optimized interface** with collapsible search on small screens

### 🌳 Custom Green Markers
- **Tree-themed icons** with custom green styling
- **Hover effects** with smooth scaling animations
- **High-contrast design** with white background and green borders
- **Responsive sizing** that adapts to different screen sizes

### 🔍 City Search Integration
- **Smart city search** with autocomplete suggestions
- **Global city database** including major cities worldwide
- **Automatic map centering** when a city is selected
- **Park filtering** showing only relevant green spaces near the selected city

### 📍 Park Information
- **Detailed tooltips** with park names, descriptions, and features
- **Park ratings** displayed with star ratings
- **Area information** showing park size and type
- **Feature lists** including amenities like playgrounds, trails, lakes, etc.

### 📱 Responsive Design
- **Mobile-first approach** with touch-friendly controls
- **Collapsible search interface** for better mobile experience
- **Adaptive text sizing** and spacing for different screen sizes
- **Optimized overlays** that don't interfere with map interaction

## Technical Implementation

### Dependencies
- `leaflet` - Core mapping library
- `react-leaflet` - React components for Leaflet
- `tailwindcss` - Utility-first CSS framework
- `lucide-react` - Icon library for UI elements

### Components Structure
```
src/components/
├── InteractiveMap.jsx      # Main map component with Leaflet integration
├── MapExplorer.jsx         # Container component with search integration
├── CitySearch.jsx          # Existing city search functionality
└── ...
```

### Key Features Implementation

#### Custom Markers
```javascript
const createTreeIcon = () => {
  return new L.DivIcon({
    html: `<div>SVG tree icon with custom styling</div>`,
    iconSize: [40, 40],
    className: 'custom-tree-marker'
  });
};
```

#### Responsive Overlays
- Position-aware overlays that adjust based on screen size
- Collapsible search interface for mobile devices
- Legend and city info panels with backdrop blur effects

#### Data Management
- Mock park data with real coordinates for major cities
- Intelligent filtering based on city proximity
- Structured park information with ratings and features

## Usage

1. **Navigate to Map Explorer** - Click the "Map Explorer" tab in the navigation
2. **Search for a City** - Use the search box to find a city
3. **Explore Green Spaces** - Click on green tree markers to see park details
4. **View Details** - Read park descriptions, ratings, and available features

## Customization

### Adding More Parks
Add new park objects to the `mockParks` array in `InteractiveMap.jsx`:

```javascript
{
  name: "Park Name",
  coordinates: [latitude, longitude],
  description: "Park description",
  type: "Park Type",
  area: "Size information",
  features: ["Feature 1", "Feature 2"],
  rating: 4.5,
  city: "City Name"
}
```

### Mapbox Integration
To use Mapbox tiles instead of OpenStreetMap:

1. Get a Mapbox API key
2. Replace the TileLayer URL in `InteractiveMap.jsx`:
```javascript
url={`https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=YOUR_MAPBOX_TOKEN`}
```

### Styling Customization
- Modify colors in `tailwind.config.js`
- Adjust marker styles in the `createTreeIcon` function
- Update CSS classes in `index.css` for map-specific styling

## Future Enhancements

- Real-time park data integration via API
- User reviews and ratings system
- Directions to parks
- Weather information overlay
- Park opening hours and amenities
- Photo galleries for each park
- Accessibility information
- Event calendar integration