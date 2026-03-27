import requests
import random
import os
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
import sounddevice as sd
from scipy.io.wavfile import write


# 1. O Motor de Áudio (Fala do Computador)
class AudioEngine:
    def play_word(self, word):
        temp_file = f"audio_temp_{random.randint(1, 1000)}.mp3"
        tts = gTTS(text=word, lang='en')
        tts.save(temp_file)
        playsound(temp_file)
        try:
            os.remove(temp_file)
        except:
            pass


# 2. O NOVO Motor de Microfone (Escuta o Usuário)
# À prova de travamentos do Windows
class SpeechEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen_english(self):
        print("\n🎤 LIGANDO MICROFONE... Fale em INGLÊS agora! (Você tem 3 segundos)")

        sample_rate = 44100
        seconds = 3

        # Grava o áudio do seu microfone
        recording = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # Espera os 3 segundos

        voice_file = 'my_voice.wav'
        write(voice_file, sample_rate, recording)

        final_text = ""

        try:
            # BLOCO 1: Apenas lê o arquivo e guarda na memória (depois fecha rápido)
            with sr.AudioFile(voice_file) as source:
                print("⏳ Processando a sua pronúncia no Google...")
                audio = self.recognizer.record(source)

            # BLOCO 2: Agora que o arquivo está fechado, manda pra internet!
            final_text = self.recognizer.recognize_google(audio, language="en-US").lower()

        except sr.UnknownValueError:
            final_text = "not_understood"
        except sr.RequestError:
            final_text = "internet_error"

        # BLOCO 3: Limpeza final com segurança (o Windows não vai mais bloquear)
        if os.path.exists(voice_file):
            try:
                os.remove(voice_file)
            except:
                pass

        return final_text


# 3. O Motor de Tradução
class TranslatorAPI:
    def get_translation(self, word):
        url = f"https://api.mymemory.translated.net/get?q={word}&langpair=en|pt"
        response = requests.get(url)
        data = response.json()
        return data['responseData']['translatedText'].strip().lower()


# 4. A Sessão do Jogo (AGORA COM O COMANDO FALAR!)
class GameSession:
    def __init__(self):
        self.xp = 0
        self.lives = 3
        self.translator = TranslatorAPI()
        self.audio = AudioEngine()
        self.mic = SpeechEngine()  # O jogo recebe o microfone!
        self.vocabulary = ["developer", "challenge", "loop", "variable", "journey"]

    def play(self):
        print("🎮 Bem-vinda ao English Quest! Traduza ou Fale para ganhar XP.")
        print("-" * 50)

        while self.lives > 0 and self.vocabulary:
            word = random.choice(self.vocabulary)
            self.vocabulary.remove(word)

            print("⏳ Buscando tradução no servidor...")
            correct_translation = self.translator.get_translation(word)

            print(f"\nHP: {'❤️' * self.lives}  |  XP: {self.xp}")
            print("🔊 Escute a pronúncia inicial...")
            self.audio.play_word(word)

            while True:
                # --- OLHA A OPÇÃO 'FALAR' AQUI! ---
                answer = input(f"Traduza '{word.upper()}' (comandos: 'dica', 'ouvir', 'falar'): ").strip().lower()

                if answer == "ouvir":
                    print("🔊 Tocando novamente...")
                    self.audio.play_word(word)
                    continue

                elif answer == "dica":
                    if self.xp >= 5:
                        self.xp -= 5
                        print(f"💡 Dica: A palavra em português começa com '{correct_translation[0].upper()}'")
                        print(f"Seu XP caiu para: {self.xp}")
                    else:
                        print("❌ Saldo insuficiente! Você precisa ter 5 XP.")
                    continue

                # --- A MECÂNICA DE VERIFICAR A PRONÚNCIA ---
                elif answer == "falar":
                    spoken_word = self.mic.listen_english()

                    if spoken_word == word:
                        self.xp += 15  # Ganha mais XP por ter coragem de falar!
                        print(f"🌟 UAU! Pronúncia perfeita! Você disse '{spoken_word}'. +15 XP")
                        break
                    elif spoken_word in ["not_understood", "silence"]:
                        print("❌ Não consegui te ouvir direito. Tente falar mais perto ou digite a tradução.")
                        continue  # Volta para o loop sem perder vida
                    elif spoken_word == "internet_error":
                        print("❌ Erro ao conectar com o Google. Tente digitar a tradução.")
                        continue
                    else:
                        self.lives -= 1
                        print(f"❌ Quase! Eu entendi '{spoken_word}', mas a palavra era '{word}'.")
                        break
                # -------------------------------------------

                elif answer == correct_translation:
                    self.xp += 10
                    print("✨ Acertou em cheio a tradução! +10 XP")
                    break

                else:
                    self.lives -= 1
                    print(f"❌ Ops! A tradução correta era: '{correct_translation.upper()}'")
                    break

        print("-" * 50)
        if self.lives == 0:
            print("💀 Game Over! Você ficou sem vidas.")
        else:
            print(f"🏆 Vitória! Você completou o nível com {self.xp} XP.")


if __name__ == "__main__":
    my_game = GameSession()
    my_game.play()