import 'package:flutter/material.dart';

/// Brand and semantic colors (UI/UX Brief, §4.1).
///
/// Locked in Round 1: warm and trustworthy — greens and cream, designed to
/// stay readable in bright outdoor sunlight.
abstract final class AppColors {
  // Brand palette
  static const Color leafGreen = Color(0xFF1B7A43); // primary actions
  static const Color softGreen = Color(0xFF4CAF50); // success / "yes"
  static const Color cream = Color(0xFFFAF6EC); // screen background
  static const Color white = Color(0xFFFFFFFF); // cards, on-green text
  static const Color ink = Color(0xFF1F2A24); // body text on cream
  static const Color stoneGrey = Color(0xFF5C6B63); // captions, secondary

  // Semantic result levels (PDF + result screens)
  static const Color green = Color(0xFF2E7D32); // normal
  static const Color amber = Color(0xFFC77800); // watch
  static const Color red = Color(0xFFC62828); // visit health center
}
