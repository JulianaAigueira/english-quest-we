from django.shortcuts import render, redirect
import requests
import random
from deep_translator import GoogleTranslator


class TranslatorAPI:
    def get_translation(self, text):
        translated_text = GoogleTranslator(source='en', target='pt').translate(text)
        return translated_text.strip().lower()


def index(request):
    translator = TranslatorAPI()

    vocabulary = [
        "water", "coffee", "breakfast", "family", "school", "money",
        "good morning", "how are you", "thank you", "good night", "see you later"
    ]

    if 'xp' not in request.session:
        request.session['xp'] = 0
        request.session['lives'] = 3
        request.session['current_word'] = random.choice(vocabulary)

    # Resgata as mensagens salvas da rodada anterior e já limpa da memória
    message = request.session.pop('message', '')
    failed_word = request.session.pop('failed_word', '')

    if request.method == 'POST':
        answer_type = request.POST.get('answer_type', 'text')
        user_answer = request.POST.get('user_answer', '').strip().lower()
        current_word = request.session['current_word']

        # TRAVA DE SEGURANÇA: Se o usuário enviar vazio, não fazemos nada!
        if not user_answer:
            request.session['message'] = "⚠️ Por favor, digite ou fale algo antes de enviar!"
            return redirect('home')

        # LÓGICA 1: O aluno usou o microfone
        if answer_type == 'voice':
            if user_answer == current_word:
                xp_gained = 25 if " " in current_word else 15
                request.session['xp'] += xp_gained
                request.session['message'] = f"🌟 UAU! Pronúncia perfeita! Você disse '{user_answer}'. +{xp_gained} XP"
            else:
                request.session['lives'] -= 1
                request.session['message'] = f"❌ Quase! Eu entendi '{user_answer}', mas a palavra era '{current_word}'."
                request.session['failed_word'] = current_word

        # LÓGICA 2: O aluno usou o teclado
        else:
            correct_translation = translator.get_translation(current_word)
            if user_answer == correct_translation:
                xp_gained = 20 if " " in current_word else 10
                request.session['xp'] += xp_gained
                request.session[
                    'message'] = f"✨ Acertou! '{current_word}' significa '{correct_translation}'. +{xp_gained} XP"
            else:
                request.session['lives'] -= 1
                request.session['message'] = f"❌ Ops! A tradução de '{current_word}' era: '{correct_translation}'"
                request.session['failed_word'] = current_word

        request.session['current_word'] = random.choice(vocabulary)

        if request.session['lives'] <= 0:
            request.session['message'] = "💀 Game Over! Você ficou sem vidas. O jogo recomeçou."
            request.session['xp'] = 0
            request.session['lives'] = 3
            if 'failed_word' in request.session:
                del request.session['failed_word']

        # A MÁGICA DO PRG: Em vez de renderizar, nós redirecionamos a página.
        # Assim o F5 apenas recarrega a página limpa, sem reenviar formulários!
        return redirect('home')

    context = {
        'word': request.session['current_word'],
        'xp': request.session['xp'],
        'lives': request.session['lives'],
        'message': message,
        'failed_word': failed_word
    }

    return render(request, 'index.html', context)