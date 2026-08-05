import 'package:flutter/material.dart';

import 'theme/app_colors.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const WellnessShieldApp());
}

class WellnessShieldApp extends StatelessWidget {
  const WellnessShieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Wellness Shield',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: const HomeShell(),
    );
  }
}

/// Phase 1 shell — proves the design system renders.
///
/// Replaced by the real Welcome → Login flow in Phase 2 (App Flow §5).
class HomeShell extends StatelessWidget {
  const HomeShell({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(flex: 2),
              Text(
                'Wellness Shield',
                textAlign: TextAlign.center,
                style: theme.textTheme.displayLarge,
              ),
              const SizedBox(height: 16),
              Text(
                'A healthy child is a happy child',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: AppColors.stoneGrey,
                ),
              ),
              const Spacer(flex: 3),
              ElevatedButton(
                // Wired to the capture flow in Phase 2.
                onPressed: () {},
                child: const Text('New Screening'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
