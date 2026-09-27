import React, { useState } from 'react';
import { ActivityIndicator, Image, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import { launchImageLibrary } from 'react-native-image-picker';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL;
const LANGUAGES = [
  ['english', 'English'], ['chinese', '中文'], ['cantonese', '廣東話'], ['hindi', 'हिन्दी'],
];

export default function App() {
  const [image, setImage] = useState(null);
  const [language, setLanguage] = useState('english');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function chooseImage() {
    launchImageLibrary({ mediaType: 'photo', selectionLimit: 1 }, (response) => {
      if (response.didCancel) return;
      if (response.errorCode) {
        setError(response.errorMessage || 'Unable to open your photos.');
        return;
      }
      const selected = response.assets && response.assets[0];
      if (selected) {
        setImage(selected);
        setResult(null);
        setError('');
      }
    });
  }

  async function processImage() {
    if (!image) return;
    if (!API_BASE_URL) {
      setError('Set EXPO_PUBLIC_API_URL to your PatientPal server URL first.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const body = new FormData();
      body.append('file', { uri: image.uri, type: image.type || 'image/jpeg', name: image.fileName || 'report.jpg' });
      body.append('language', language);
      const response = await fetch(`${API_BASE_URL.replace(/\/$/, '')}/upload`, { method: 'POST', body });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to process this image.');
      setResult(data.report);
    } catch (requestError) {
      setError(requestError.message || 'Unable to reach PatientPal.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.page}>
        <Text style={styles.brand}>✳  patientpal</Text>
        <Text style={styles.eyebrow}>YOUR REPORT, MADE CLEARER</Text>
        <Text style={styles.title}>Understand your{'\n'}<Text style={styles.titleAccent}>health documents.</Text></Text>
        <Text style={styles.intro}>A plain-language summary and translation from a photo of your report.</Text>

        <View style={styles.card}>
          <Text style={styles.eyebrow}>01 · ADD A DOCUMENT</Text>
          <Pressable accessibilityRole="button" onPress={chooseImage} style={styles.pickButton}>
            {image ? <Image source={{ uri: image.uri }} style={styles.preview} /> : <Text style={styles.uploadIcon}>↑</Text>}
            <Text style={styles.pickTitle}>{image ? image.fileName || 'Photo selected' : 'Choose a photo'}</Text>
            <Text style={styles.hint}>PNG, JPG, or WebP · up to 8 MB</Text>
          </Pressable>

          <Text style={styles.label}>TRANSLATE INTO</Text>
          <View style={styles.languages}>
            {LANGUAGES.map(([code, label]) => (
              <Pressable key={code} accessibilityRole="radio" accessibilityState={{ selected: language === code }} onPress={() => setLanguage(code)} style={[styles.language, language === code && styles.languageSelected]}>
                <Text style={[styles.languageText, language === code && styles.languageTextSelected]}>{label}</Text>
              </Pressable>
            ))}
          </View>
          <Pressable accessibilityRole="button" disabled={!image || loading} onPress={processImage} style={[styles.submit, (!image || loading) && styles.disabled]}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.submitText}>Make it clearer  →</Text>}
          </Pressable>
          <Text style={styles.privacy}>This app doesn’t save your image. Google Gemini processes it; gTTS receives translated text to create audio.</Text>
        </View>

        <View style={styles.card} accessibilityLiveRegion="polite">
          <Text style={styles.eyebrow}>02 · YOUR RESULTS</Text>
          <Text style={styles.sectionTitle}>Your report, made clearer</Text>
          {loading && <Text style={styles.hint}>Reading your document…</Text>}
          {!!error && <Text accessibilityRole="alert" style={styles.error}>{error}</Text>}
          {result && <>
            <Text style={styles.label}>PLAIN-LANGUAGE SUMMARY</Text><Text style={styles.output}>{result.summary}</Text>
            <Text style={styles.label}>TRANSLATION</Text><Text style={styles.output}>{result.translation}</Text>
            <Text style={styles.hint}>This mobile prototype shows text only. Open the web app to listen to the translation.</Text>
          </>}
          {!result && !loading && !error && <Text style={styles.hint}>Your summary and translation will appear here.</Text>}
          <Text style={styles.disclaimer}>For understanding documents only. This is not medical advice.</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#f4f7f5' }, page: { padding: 22, paddingBottom: 42 },
  brand: { color: '#1f4037', fontSize: 20, fontWeight: '800', marginBottom: 44 },
  eyebrow: { color: '#52816e', fontSize: 10, fontWeight: '700', letterSpacing: 1.3, marginBottom: 10 },
  title: { color: '#193b32', fontSize: 36, lineHeight: 42, fontWeight: '800', letterSpacing: -1.5 },
  titleAccent: { color: '#5b967c' }, intro: { color: '#71827b', fontSize: 14, lineHeight: 22, marginTop: 13, marginBottom: 27 },
  card: { backgroundColor: '#fff', borderColor: '#e6ece8', borderWidth: 1, borderRadius: 16, padding: 20, marginBottom: 15 },
  pickButton: { minHeight: 155, alignItems: 'center', justifyContent: 'center', borderStyle: 'dashed', borderWidth: 1, borderColor: '#c8d9cf', backgroundColor: '#f8fbf8', borderRadius: 13, padding: 12 },
  uploadIcon: { color: '#418163', backgroundColor: '#e6f1e9', overflow: 'hidden', borderRadius: 13, fontSize: 28, paddingHorizontal: 13, paddingVertical: 4, marginBottom: 8 },
  preview: { width: 82, height: 82, borderRadius: 12, marginBottom: 8 }, pickTitle: { color: '#34564a', fontWeight: '700' }, hint: { color: '#899890', fontSize: 11, lineHeight: 17, marginTop: 5 },
  label: { color: '#768a80', fontSize: 9, letterSpacing: 1, fontWeight: '700', marginTop: 19, marginBottom: 8 },
  languages: { flexDirection: 'row', flexWrap: 'wrap', gap: 7 }, language: { borderWidth: 1, borderColor: '#dfe8e2', borderRadius: 8, paddingVertical: 8, paddingHorizontal: 11 }, languageSelected: { backgroundColor: '#eaf3ec', borderColor: '#6da287' }, languageText: { color: '#60776c', fontSize: 12 }, languageTextSelected: { color: '#2e7055', fontWeight: '700' },
  submit: { backgroundColor: '#32765d', borderRadius: 9, minHeight: 46, justifyContent: 'center', alignItems: 'center', marginTop: 17 }, disabled: { opacity: .55 }, submitText: { color: '#fff', fontWeight: '700', fontSize: 13 }, privacy: { color: '#899890', fontSize: 10, lineHeight: 15, marginTop: 15 },
  sectionTitle: { color: '#234238', fontSize: 18, fontWeight: '700', marginBottom: 12 }, output: { color: '#435d52', fontSize: 13, lineHeight: 21, marginBottom: 5 }, error: { color: '#9c493a', backgroundColor: '#fff4f0', padding: 11, borderRadius: 8, marginTop: 12 }, disclaimer: { color: '#9aa79f', fontSize: 10, lineHeight: 15, borderTopColor: '#edf1ee', borderTopWidth: 1, marginTop: 18, paddingTop: 12 },
});
