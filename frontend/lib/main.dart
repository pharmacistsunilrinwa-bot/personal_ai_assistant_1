import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';

void main() {
  runApp(PersonalAIApp());
}

class PersonalAIApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Personal AI Assistant',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: ChatScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ChatScreen extends StatefulWidget {
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final TextEditingController _urlController = TextEditingController();
  final List<Map<String, String>> _messages = [];
  final stt.SpeechToText _speech = stt.SpeechToText();
  final FlutterTts _tts = FlutterTts();
  
  bool _isListening = false;
  bool _isThinking = false;
  bool _showSettings = false;
  
  // Default URL is set to localhost / standard emulator loopback, but easily configurable in UI
  String _baseUrl = "http://10.0.2.2:8000/api/v1"; 

  @override
  void initState() {
    super.initState();
    _urlController.text = _baseUrl;
    _initSpeech();
  }

  void _initSpeech() async {
    try {
      await _speech.initialize();
    } catch (e) {
      print("Speech initialization error: $e");
    }
  }

  Future<void> _sendMessage(String text) async {
    if (text.isEmpty) return;

    setState(() {
      _messages.add({"role": "user", "content": text});
      _isThinking = true;
    });

    try {
      final response = await http.post(
        Uri.parse("$_baseUrl/chat"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"message": text}),
      ).timeout(const Duration(seconds: 15)); // 15 seconds timeout to prevent hanging

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final aiResponse = data['response'] ?? "No response received.";
        setState(() {
          _messages.add({"role": "ai", "content": aiResponse});
        });
        await _tts.speak(aiResponse);
      } else {
        // Handle server errors (e.g. 500, 404, 401)
        setState(() {
          _messages.add({
            "role": "error",
            "content": "Error: Server returned status code ${response.statusCode}.\n"
                        "Please verify that your Backend URL is correct and the server is running."
          });
        });
      }
    } on TimeoutException catch (_) {
      setState(() {
        _messages.add({
          "role": "error",
          "content": "Connection Timeout: The server took too long to respond.\n"
                      "Please ensure your tunnel (Localtunnel/Ngrok) is active and reachable."
        });
      });
    } catch (e) {
      // Handle network exceptions (e.g. SocketException, HostNotFound)
      setState(() {
        _messages.add({
          "role": "error",
          "content": "Connection Failed: Could not reach the backend.\n"
                      "Details: $e\n\n"
                      "Please verify:\n"
                      "1. Your Backend URL is configured correctly.\n"
                      "2. Your phone/emulator has internet access.\n"
                      "3. Your local server and tunnel are running."
        });
      });
    } finally {
      setState(() {
        _isThinking = false;
      });
    }
  }

  void _listen() async {
    if (!_isListening) {
      bool available = await _speech.initialize();
      if (available) {
        setState(() => _isListening = true);
        _speech.listen(onResult: (val) {
          if (val.finalResult) {
            setState(() => _isListening = false);
            _controller.text = val.recognizedWords;
            _sendMessage(val.recognizedWords);
          }
        });
      }
    } else {
      setState(() => _isListening = false);
      _speech.stop();
    }
  }

  Future<void> _pickFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles();
      if (result != null && result.files.single.path != null) {
        File file = File(result.files.single.path!);
        _sendMessage("I uploaded a file: ${result.files.single.name}. Please analyze it.");
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Failed to pick file: $e")),
      );
    }
  }

  void _saveUrl() {
    setState(() {
      _baseUrl = _urlController.text.trim();
      _showSettings = false;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Backend URL updated to: $_baseUrl")),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Personal AI Assistant"),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
        actions: [
          IconButton(
            icon: Icon(_showSettings ? Icons.close : Icons.settings),
            onPressed: () {
              setState(() {
                _showSettings = !_showSettings;
              });
            },
            tooltip: "Configure Backend URL",
          )
        ],
      ),
      body: Column(
        children: [
          if (_showSettings) _buildSettingsPanel(),
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final role = msg['role'];
                final content = msg['content'] ?? "";
                
                if (role == 'error') {
                  return _buildErrorCard(content);
                }

                final isUser = role == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    maxWidth: MediaQuery.of(context).size.width * 0.75,
                    margin: EdgeInsets.symmetric(vertical: 4),
                    padding: EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: isUser 
                          ? Theme.of(context).colorScheme.primary
                          : Theme.of(context).colorScheme.surfaceVariant,
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(16),
                        topRight: Radius.circular(16),
                        bottomLeft: isUser ? Radius.circular(16) : Radius.zero,
                        bottomRight: isUser ? Radius.zero : Radius.circular(16),
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.05),
                          blurRadius: 3,
                          offset: Offset(0, 1),
                        )
                      ]
                    ),
                    child: Text(
                      content,
                      style: TextStyle(
                        color: isUser 
                            ? Theme.of(context).colorScheme.onPrimary
                            : Theme.of(context).colorScheme.onSurfaceVariant,
                        fontSize: 15,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          if (_isThinking) _buildThinkingIndicator(),
          _buildInputPanel(),
        ],
      ),
    );
  }

  Widget _buildSettingsPanel() {
    return Card(
      margin: EdgeInsets.all(12),
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              "Backend Connection Configuration",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
            SizedBox(height: 8),
            Text(
              "For emulators, use: http://10.0.2.2:8000/api/v1\n"
              "For real devices, run 'lt --port 8000' and paste the URL here.",
              style: TextStyle(fontSize: 12, color: Colors.grey[700]),
            ),
            SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _urlController,
                    decoration: InputDecoration(
                      labelText: "Backend Base URL",
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                  ),
                ),
                SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _saveUrl,
                  child: Text("Save"),
                )
              ],
            )
          ],
        ),
      ),
    );
  }

  Widget _buildErrorCard(String errorText) {
    return Card(
      color: Theme.of(context).colorScheme.errorContainer,
      margin: EdgeInsets.symmetric(vertical: 8, horizontal: 4),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.error_outline, color: Theme.of(context).colorScheme.error),
            SizedBox(width: 10),
            Expanded(
              child: Text(
                errorText,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onErrorContainer,
                  fontSize: 13,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildThinkingIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Row(
        children: [
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          SizedBox(width: 10),
          Text(
            "AI is reasoning...",
            style: TextStyle(
              fontSize: 13,
              fontStyle: FontStyle.italic,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputPanel() {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 5,
            offset: Offset(0, -2),
          )
        ],
      ),
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6.0),
      child: SafeArea(
        child: Row(
          children: [
            IconButton(
              icon: Icon(Icons.attach_file, color: Theme.of(context).colorScheme.primary),
              onPressed: _pickFile,
              tooltip: "Attach File",
            ),
            Expanded(
              child: TextField(
                controller: _controller,
                decoration: InputDecoration(
                  hintText: "Ask me anything...",
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                ),
                textInputAction: TextInputAction.send,
                onSubmitted: (text) {
                  _sendMessage(text);
                  _controller.clear();
                },
              ),
            ),
            IconButton(
              icon: Icon(_isListening ? Icons.mic : Icons.mic_none),
              color: _isListening ? Colors.red : Theme.of(context).colorScheme.primary,
              onPressed: _listen,
              tooltip: "Voice Input",
            ),
            IconButton(
              icon: Icon(Icons.send),
              color: Theme.of(context).colorScheme.primary,
              onPressed: () {
                _sendMessage(_controller.text);
                _controller.clear();
              },
              tooltip: "Send Message",
            ),
          ],
        ),
      ),
    );
  }
}
