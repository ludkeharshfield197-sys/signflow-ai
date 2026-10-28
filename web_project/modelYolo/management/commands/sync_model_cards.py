from django.core.management.base import BaseCommand

from inference.evaluation_cards import evaluation_card_for
from modelYolo.models import YoloModel


class Command(BaseCommand):
    help = "Attach verified local evaluation cards to registered model records."

    def handle(self, *args, **options):
        updated = 0
        for model in YoloModel.objects.all().iterator():
            card = evaluation_card_for(model.file_path)
            fields = []
            if card and model.evaluation != card:
                model.evaluation = card
                fields.append("evaluation")
            if model.remark != "本地多类别手语识别模型":
                model.remark = "本地多类别手语识别模型"
                fields.append("remark")
            if fields:
                model.save(update_fields=fields)
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Synchronized {updated} model card(s)."))
