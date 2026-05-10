from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from exams.services.import_question_bank import (
    QuestionBankImportError,
    import_question_bank,
)


class Command(BaseCommand):
    help = "Import product_research/question_bank.json into Django models."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to question_bank.json")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and report expected counts without writing content rows.",
        )
        parser.add_argument(
            "--replace-existing",
            action="store_true",
            help="Overwrite existing imported rows by source ID.",
        )
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help="Mark imported content inactive when it is missing from the source file.",
        )

    def handle(self, *args, **options):
        try:
            summary = import_question_bank(
                options["path"],
                dry_run=options["dry_run"],
                replace_existing=options["replace_existing"],
                deactivate_missing=options["deactivate_missing"],
            )
        except (OSError, ValueError, QuestionBankImportError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS("Question bank import completed."))
        for label, values in summary.as_dict().items():
            self.stdout.write(f"{label}: {values}")
