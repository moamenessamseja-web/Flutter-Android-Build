import 'package:flutter/material.dart';

void main() => runApp(const SmokeApp());

class SmokeApp extends StatelessWidget {
  const SmokeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: Scaffold(body: Center(child: Text('Smoke OK'))),
    );
  }
}
