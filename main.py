import ec2_controller
import s3_uploader
import cloudwatch_alerts

print("=" * 50)
print("AWS Python Automation Suite")
print("Author: Sadhvi - Cloud Engineer")
print("=" * 50)

print("\n--- Running EC2 Controller ---")
ec2_controller.check_and_control()

print("\n--- Running S3 Uploader ---")
s3_uploader.run()

print("\n--- Running CloudWatch Alerts ---")
cloudwatch_alerts.run()

print("\n--- All automation tasks complete! ---")