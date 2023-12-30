import csv
import re
import genanki
import random
import argparse

from pathlib import Path
from gtts import gTTS

parser = argparse.ArgumentParser(
                    prog='Create Anki Deck',
                    description='Program creates a apkg deck file')


def check_file_extension(filename: str):
    if not filename.endswith('.csv'):
        parser.error('argument must have a .csv extension')
    return filename


parser.add_argument('-d', '--deck', required=True)
parser.add_argument('-l', '--lang', required=True)
parser.add_argument('-f', '--csv',
                    required=True,
                    type=lambda s: check_file_extension(s))

args = parser.parse_args()

cwd = Path.cwd()
sounds_dir = cwd / 'sounds'
sounds_dir.mkdir(exist_ok=True)


def generate_id():
    return random.randint(10000, 99999)


deck = genanki.Deck(
    generate_id(),
    args.deck
)

package = genanki.Package(deck)

model = genanki.Model(
  generate_id(),
  'Model w/ Media',
  fields=[
    {'name': 'Front'},
    {'name': 'Back'},
    {'name': 'Media'}
  ],
  templates=[
    {
      'name': 'Card',
      'qfmt': '<center>{{Front}} {{Media}}</center>',
      'afmt': '<center>{{FrontSide}}<hr id="answer">{{Back}}</center>',
    },
  ])


def create_audio_file(sentence: str, audio_path: str, lang: str) -> None:
    tts = gTTS(sentence, lang=lang)
    tts.save(audio_path)


def add_audio_path_to_package_media_files(audio_path: str) -> None:
    package.media_files.append(audio_path)


def create_card(sentence: str, translation: str, file: str) -> None:
    note = genanki.Note(
        model=model,
        fields=[sentence, translation, f'[sound:{file}]']
    )
    deck.add_note(note)


def remove_special_chars(text: str) -> str:
    return re.sub(r'[.,!¿?/\'-="\\]', '', text)


with open(cwd / f'{args.csv}', 'r') as file:
    reader = csv.reader(file, delimiter=';')
    for line in reader:
        sentence, translation = line
        filename = f'{remove_special_chars(sentence)}.mp3'
        audio_path = sounds_dir / filename
        create_audio_file(sentence, audio_path, args.lang)
        add_audio_path_to_package_media_files(audio_path)
        create_card(sentence, translation, audio_path)

package.write_to_file(f'{args.deck}.apkg')
