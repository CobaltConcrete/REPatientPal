import React from 'react';
import { Button, Image, View } from 'react-native';
import { launchImageLibrary } from 'react-native-image-picker';

export default function App() {
  const [imageUri, setImageUri] = React.useState(null);

  const selectImage = () => {
    launchImageLibrary({ mediaType: 'photo' }, (response) => {
      if (response.assets && response.assets.length > 0) {
        const image = response.assets[0];
        setImageUri(image.uri);

        // If you want to send the image to a server
        const data = new FormData();
        data.append('image', {
          uri: image.uri,
          type: image.type,
          name: image.fileName,
        });

        fetch('http://127.0.0.1:5000/process-image', {
          method: 'POST',
          body: data,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
      }
    });
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Button title="Select Image" onPress={selectImage} />
      {imageUri && <Image source={{ uri: imageUri }} style={{ width: 300, height: 300 }} />}
    </View>
  );
}
