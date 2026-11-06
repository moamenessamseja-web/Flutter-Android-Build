import 'package:flutter_test/flutter_test.dart';
import 'package:smoke_app/main.dart';

void main() {
  testWidgets('shows the smoke text', (tester) async {
    await tester.pumpWidget(const SmokeApp());
    expect(find.text('Smoke OK'), findsOneWidget);
  });
}
