"""Run every automation task in sequence.

Each task module now guards its own entry point, so importing one no longer
executes it. That matters here specifically: without those guards, `import
ec2_controller` ran the task once as a side effect of the import and the
explicit `ec2_controller.check_and_control()` below ran it a second time --
every task in this suite executed twice per invocation.
"""
import cloudwatch_alerts
import ec2_controller
import s3_uploader


def run_all() -> None:
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


if __name__ == "__main__":
    run_all()
