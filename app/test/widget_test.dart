import 'package:flutter_test/flutter_test.dart';

import 'package:wellness_shield/main.dart';

void main() {
  testWidgets('renders the Phase 1 home shell', (WidgetTester tester) async {
    await tester.pumpWidget(const WellnessShieldApp());

    expect(find.text('Wellness Shield'), findsOneWidget);
    expect(find.text('New Screening'), findsOneWidget);
  });
}
