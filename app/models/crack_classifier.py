import torch
import torch.nn as nn
from torchvision import transforms
import timm
from PIL import Image
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best_model.pth')

CONFIG = {
    'img_size': 224,
    'num_classes': 2,
    'dropout': 0.2
}

CLASS_LABELS = {0: "Negative (No Crack)", 1: "Positive (Crack Detected)"}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class CrackClassifier(nn.Module):
    def __init__(self, num_classes=2, pretrained=False, dropout=0.2):
        super().__init__()
        self.backbone = timm.create_model(
            'mobilenetv3_large_100',
            pretrained=pretrained,
            num_classes=0,
            drop_rate=dropout
        )
        self.feature_dim = 1280
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(self.feature_dim, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, num_classes)
        )
        self._init_classifier()

    def _init_classifier(self):
        for m in self.classifier.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        if x.dim() == 3:
            x = x.unsqueeze(0)
        features = self.backbone(x)
        return self.classifier(features)

inference_transforms = transforms.Compose([
    transforms.Resize((CONFIG['img_size'], CONFIG['img_size'])),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

model = CrackClassifier(num_classes=CONFIG['num_classes'],
                        pretrained=False, dropout=CONFIG['dropout'])

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()
