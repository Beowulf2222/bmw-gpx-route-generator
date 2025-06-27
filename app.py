// BMW GPX Route Generator - React Native App Structure
// This shows how to convert your Streamlit app to React Native for iPhone

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  TextInput,
  Switch,
  Picker
} from 'react-native';
import MapView, { Polyline, Marker } from 'react-native-maps';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';

// BMW Bike Database (same as your Streamlit app)
const BMW_BIKES = {
  "R 1250 GS": {"tank_capacity": 20, "fuel_consumption": 5.5, "comfort_stops": 2.5, "type": "adventure"},
  "R 1250 GS Adventure": {"tank_capacity": 30, "fuel_consumption": 6.0, "comfort_stops": 3.0, "type": "adventure"},
  "R 1250 RT": {"tank_capacity": 25, "fuel_consumption": 5.8, "comfort_stops": 3.5, "type": "touring"},
  // ... rest of your BMW bikes
};

// Route Templates (same as your Streamlit app)
const ROUTE_TEMPLATES = {
  "Mountain Twisties": {
    "description": "Challenging mountain roads with tight curves",
    "terrain": "mountain",
    "difficulty": "advanced",
    "scenic_factor": 1.4,
    "waypoint_factor": 1.3
  },
  // ... rest of your templates
};

const BMWGPXApp = () => {
  // State management (equivalent to Streamlit session state)
  const [selectedBike, setSelectedBike] = useState("Select Your BMW");
  const [selectedTemplate, setSelectedTemplate] = useState("Custom Route");
  const [rideName, setRideName] = useState("My BMW Route");
  const [duration, setDuration] = useState(3);
  const [startLocation, setStartLocation] = useState({
    latitude: 42.3889,
    longitude: -71.1294
  });
  const [routeCoordinates, setRouteCoordinates] = useState([]);
  const [emergencyContact, setEmergencyContact] = useState("");
  const [emergencyPhone, setEmergencyPhone] = useState("");
  const [avoidTolls, setAvoidTolls] = useState(false);
  const [avoidHighways, setAvoidHighways] = useState(false);

  // Generate route function (calls your API)
  const generateRoute = async () => {
    try {
      const coordinates = generateCoordinatesFromTemplate(
        startLocation,
        selectedTemplate,
        duration
      );

      const response = await fetch('https://api.openrouteservice.org/v2/directions/driving-car/gpx', {
        method: 'POST',
        headers: {
          'Authorization': 'YOUR_API_KEY', // Store securely
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          coordinates: coordinates,
          format: 'gpx',
          instructions: true,
          elevation: true
        })
      });

      const gpxData = await response.text();
      const routeCoords = parseGPXToCoordinates(gpxData);
      setRouteCoordinates(routeCoords);

      // Generate and save GPX file
      await saveGPXFile(gpxData);
      
      Alert.alert("Success", "BMW GPX route generated and saved!");
    } catch (error) {
      Alert.alert("Error", "Failed to generate route: " + error.message);
    }
  };

  // Helper function to generate coordinates based on template
  const generateCoordinatesFromTemplate = (start, template, hours) => {
    const templateConfig = ROUTE_TEMPLATES[template];
    const radiusKm = hours * 25 * (templateConfig?.scenic_factor || 1.0);
    const numPoints = Math.floor(8 * (templateConfig?.waypoint_factor || 1.0));

    const coordinates = [[start.longitude, start.latitude]];
    
    for (let i = 0; i < numPoints; i++) {
      const angle = (2 * Math.PI * i) / numPoints;
      const radiusVariation = radiusKm * (0.7 + 0.6 * Math.sin(angle * 2));
      
      const dx = radiusVariation * Math.cos(angle);
      const dy = radiusVariation * Math.sin(angle);
      
      const latOffset = start.latitude + (dy / 111);
      const lonOffset = start.longitude + (dx / (111 * Math.cos(start.latitude * Math.PI / 180)));
      
      coordinates.push([lonOffset, latOffset]);
    }
    
    coordinates.push([start.longitude, start.latitude]); // Close loop
    return coordinates;
  };

  // Parse GPX to coordinates for map display
  const parseGPXToCoordinates = (gpxText) => {
    // Simple GPX parsing - in production use a proper XML parser
    const coords = [];
    const regex = /<trkpt lat="([^"]+)" lon="([^"]+)">/g;
    let match;
    
    while ((match = regex.exec(gpxText)) !== null) {
      coords.push({
        latitude: parseFloat(match[1]),
        longitude: parseFloat(match[2])
      });
    }
    
    return coords;
  };

  // Save GPX file with BMW metadata
  const saveGPXFile = async (gpxContent) => {
    const enhancedGPX = addBMWMetadata(gpxContent);
    const fileName = `${rideName.replace(' ', '_')}.gpx`;
    const fileUri = FileSystem.documentDirectory + fileName;
    
    await FileSystem.writeAsStringAsync(fileUri, enhancedGPX);
    
    // Share file (can be imported to BMW apps)
    if (await Sharing.isAvailableAsync()) {
      await Sharing.shareAsync(fileUri);
    }
  };

  // Add BMW-specific metadata to GPX
  const addBMWMetadata = (gpxContent) => {
    // Add BMW metadata similar to your Streamlit function
    const metadata = `
    <metadata>
      <name>${rideName}</name>
      <desc>BMW Motorrad route for ${selectedBike}</desc>
      <extensions>
        <bmw>
          <bike_model>${selectedBike}</bike_model>
          <emergency_contact>${emergencyContact}</emergency_contact>
          <emergency_phone>${emergencyPhone}</emergency_phone>
        </bmw>
      </extensions>
    </metadata>`;
    
    return gpxContent.replace('<metadata>', metadata);
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🏍️ BMW Motorrad GPX Builder</Text>
        <Text style={styles.subtitle}>Create routes for "Make Life a Ride"</Text>
      </View>

      {/* BMW Bike Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏍️ Your BMW Motorrad</Text>
        <Picker
          selectedValue={selectedBike}
          onValueChange={setSelectedBike}
          style={styles.picker}
        >
          {Object.keys(BMW_BIKES).map(bike => (
            <Picker.Item key={bike} label={bike} value={bike} />
          ))}
        </Picker>
      </View>

      {/* Route Templates */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🗺️ Route Template</Text>
        <View style={styles.templateGrid}>
          {Object.entries(ROUTE_TEMPLATES).map(([name, config]) => (
            <TouchableOpacity
              key={name}
              style={[
                styles.templateButton,
                selectedTemplate === name && styles.selectedTemplate
              ]}
              onPress={() => setSelectedTemplate(name)}
            >
              <Text style={styles.templateName}>{name}</Text>
              <Text style={styles.templateDesc}>{config.description}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Map */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📍 Route Map</Text>
        <MapView
          style={styles.map}
          region={{
            latitude: startLocation.latitude,
            longitude: startLocation.longitude,
            latitudeDelta: 0.5,
            longitudeDelta: 0.5,
          }}
          onPress={(e) => setStartLocation(e.nativeEvent.coordinate)}
        >
          <Marker coordinate={startLocation} title="Start/Finish" />
          {routeCoordinates.length > 0 && (
            <Polyline
              coordinates={routeCoordinates}
              strokeColor="#0066CC"
              strokeWidth={4}
            />
          )}
        </MapView>
      </View>

      {/* Route Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚙️ Route Settings</Text>
        
        <TextInput
          style={styles.textInput}
          placeholder="Route Name"
          value={rideName}
          onChangeText={setRideName}
        />
        
        <View style={styles.sliderContainer}>
          <Text>Duration: {duration} hours</Text>
          {/* Add slider component here */}
        </View>

        <View style={styles.switchContainer}>
          <Text>Avoid Toll Roads</Text>
          <Switch value={avoidTolls} onValueChange={setAvoidTolls} />
        </View>

        <View style={styles.switchContainer}>
          <Text>Avoid Highways</Text>
          <Switch value={avoidHighways} onValueChange={setAvoidHighways} />
        </View>
      </View>

      {/* Safety Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🛡️ Emergency Contact</Text>
        
        <TextInput
          style={styles.textInput}
          placeholder="Emergency Contact Name"
          value={emergencyContact}
          onChangeText={setEmergencyContact}
        />
        
        <TextInput
          style={styles.textInput}
          placeholder="Emergency Phone (+1-555-0123)"
          value={emergencyPhone}
          onChangeText={setEmergencyPhone}
          keyboardType="phone-pad"
        />
      </View>

      {/* Generate Button */}
      <TouchableOpacity style={styles.generateButton} onPress={generateRoute}>
        <Text style={styles.generateButtonText}>🏍️ Generate BMW Route</Text>
      </TouchableOpacity>

      {/* BMW Integration Info */}
      <View style={styles.infoSection}>
        <Text style={styles.infoTitle}>📱 BMW App Integration</Text>
        <Text style={styles.infoText}>
          • Import GPX directly to "Make Life a Ride" app{'\n'}
          • Compatible with BMW ConnectedRide{'\n'}
          • Sync with BMW Navigation system
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#0066CC',
    padding: 20,
    paddingTop: 50,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    textAlign: 'center',
    marginTop: 5,
  },
  section: {
    backgroundColor: 'white',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  picker: {
    backgroundColor: '#f0f0f0',
    borderRadius: 5,
  },
  templateGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  templateButton: {
    flex: 1,
    minWidth: 150,
    padding: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 5,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedTemplate: {
    borderColor: '#0066CC',
    backgroundColor: '#e6f3ff',
  },
  templateName: {
    fontWeight: 'bold',
    fontSize: 14,
  },
  templateDesc: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  map: {
    height: 300,
    borderRadius: 10,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 10,
    marginBottom: 10,
    backgroundColor: 'white',
  },
  sliderContainer: {
    marginBottom: 15,
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  generateButton: {
    backgroundColor: '#0066CC',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  generateButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  infoSection: {
    backgroundColor: '#e6f3ff',
    margin: 10,
    padding: 15,
    borderRadius: 10,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#0066CC',
    marginBottom: 5,
  },
  infoText: {
    color: '#0066CC',
    lineHeight: 20,
  },
});

export default BMWGPXApp;