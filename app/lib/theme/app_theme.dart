import 'package:flutter/material.dart';

import 'app_colors.dart';

/// Central theme for the app (UI/UX Brief, §4 and §11).
///
/// Typography follows §4.2: very large type (body 22–24 sp, buttons 28–32 sp
/// bold, titles 32–36 sp bold) — readable in sunlight and by older eyes.
/// Noto Sans (Latin + Devanagari) will be bundled with the asset pipeline in
/// Phase 2; the `fontFamily` constant is kept here so the theme can be wired
/// to it in one place once the font files land.
abstract final class AppTheme {
  static const String fontFamily = 'NotoSans';

  static ThemeData get light {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: AppColors.leafGreen,
    ).copyWith(
      primary: AppColors.leafGreen,
      onPrimary: AppColors.white,
      secondary: AppColors.softGreen,
      onSecondary: AppColors.white,
      surface: AppColors.white,
      onSurface: AppColors.ink,
      error: AppColors.red,
      onError: AppColors.white,
    );

    final textTheme = TextTheme(
      displayLarge: const TextStyle(
        fontSize: 36,
        fontWeight: FontWeight.w700,
        color: AppColors.ink,
        height: 1.2,
      ),
      headlineMedium: const TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.w700,
        color: AppColors.ink,
        height: 1.25,
      ),
      titleLarge: const TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.w700,
        color: AppColors.ink,
        height: 1.3,
      ),
      bodyLarge: const TextStyle(
        fontSize: 24,
        color: AppColors.ink,
        height: 1.4,
      ),
      bodyMedium: const TextStyle(
        fontSize: 22,
        color: AppColors.ink,
        height: 1.4,
      ),
      labelLarge: const TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.w700,
        color: AppColors.white,
      ),
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: AppColors.cream,
      textTheme: textTheme,
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.leafGreen,
          foregroundColor: AppColors.white,
          minimumSize: const Size.fromHeight(96),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: textTheme.labelLarge,
        ),
      ),
      cardTheme: const CardThemeData(
        color: AppColors.white,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(16)),
        ),
      ),
    );
  }
}
