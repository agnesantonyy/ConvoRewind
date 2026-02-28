from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Tone detection data ──────────────────────────────────────────────────────

AGGRESSIVE_WORDS = [
    "don't care", "hate", "stupid", "idiot", "shut up", "worthless",
    "useless", "terrible", "worst", "always", "never", "obviously",
    "clearly", "whatever", "forget it", "seriously", "unbelievable",
    "ridiculous", "pathetic", "disgusting", "annoying", "lazy",
    "you never", "you always","misery","sucks","garbage","trash","horrible","awful","dumb","screw you",
]

PASSIVE_WORDS = [
    "i guess", "maybe", "i suppose", "whatever you want", "i don't know",
    "if you say so", "fine", "i just", "nothing", "nevermind",
    "forget it", "doesn't matter", "it's okay", "do i even", "i just don't"
]

RULES = [
    {
        "match": ["don't care","I don't care what you think.",],
        "tone": "aggressive", "emoji": "🥶", "label": "Dismissive 🥶",
        "why": "Saying someone things like these dismisses their feelings before they can explain.",
        "rewrite": "I am not in a good place to talk about this right now, but I want to understand your perspective when I'm ready.",
        "tip": "Assume intent before assuming neglect."
    },
    {
        "match": [ "never","never possible","can't ever","hate it when"],
        "tone": "aggressive", "emoji": "🔥", "label": "Aggressive 🔥",
        "why": "'never' feel like verdict — they put people on the defensive instantly.",
        "rewrite": "I've noticed a pattern lately that's been bothering me. Can we talk about it?",
        "tip": "Swap 'never' for 'lately' or 'sometimes'."
    },
    {
        "match": ["whatever", "forget it"],
        "tone": "passive", "emoji": "😶", "label": "Passive-Aggressive 😶",
        "why": "Shutting down with 'whatever' signals contempt and leaves no way to respond.",
        "rewrite": "I need a moment to gather my thoughts — can we revisit this soon?",
        "tip": "A pause is better than a dismissal."
    },
    {
        "match": ["i guess", "i suppose"],
        "tone": "passive", "emoji": "😔", "label": "confusion😶",
        "why": "Hedging with 'I guess' signals reluctant agreement and breeds hidden resentment.",
        "rewrite": "I'm not fully on board yet — can I share my concern when I'm ready?",
        "tip": "Say what you mean, even if it's uncomfortable when you're shure about it, else communicate when you're ready."
    },
    {
        "match": ["fine","okay", "it's okay", "i'll try","if you say so"],
        "tone": "neutral", "emoji": "🙂", "label": "Neutral/Endurance😶",
        "why": "'Fine','okay' rarely means fine — it's a signal of unspoken frustration that festers.",
        "rewrite": "If you're uncomfortable while saying you are okay with what's going on, try if you can open up about how you feel.",
        "tip": "Replace 'fine' with your actual feeling."
    },
    {
        "match": ["ridiculous", "pathetic", "stupid", "idiot","usesless","terrible","worst","seriously","ridiculous","annoying","lazy""I don't care what you think", "You never listen to me", "You always mess things up", "This is completely your fault", "I can't believe you did that", "Why do you always act like this", "That was such a bad decision", "You clearly don't understand", "I'm tired of your excuses", "This is ridiculous", "You make everything worse", "I expected better from you", "That was the worst choice you could have made", "You don't even try", "I'm done explaining this", "You're impossible to deal with", "Stop pretending you don't know", "You just don't get it", "This is why nobody trusts you", "I shouldn't have to repeat myself", "You ruined it", "That's not my problem", "Whatever, do what you want", "I don't have time for this", "You're overreacting again", "Why are you like this", "This conversation is pointless", "I knew you would mess this up", "You never take responsibility", "That was a terrible idea", "I can't stand this anymore", "You clearly weren't thinking", "This is on you", "You made it worse", "That's the worst idea I've heard", "You're not even trying to understand", "This is a waste of time", "I don't owe you anything", "You always blame others", "I'm not surprised you failed", "You disappoint me every time", "You don't care about anyone but yourself", "This is why I don't trust you", "You just don't think things through", "You handled that badly", "You're being unreasonable", "I'm sick of this", "You made the same mistake again", "I can't rely on you", "You completely ignored what I said", "You always twist my words", "This is getting on my nerves", "You don't take anything seriously", "I shouldn't have expected more", "You're making excuses again", "You always make it about yourself", "You don't respect my time", "You made this harder than it needed to be", "You never admit when you're wrong", "I'm tired of cleaning up your mess", "You clearly didn't think this through", "This is exactly the problem with you", "You can't handle simple tasks", "You don't even try to improve", "You act like nothing is your fault", "You turned this into a disaster", "You don't value my effort", "You never appreciate anything", "You're impossible to please", "You always overcomplicate things", "You just don't care", "This is pointless because of you", "You handled that poorly", "You made the wrong call again", "You're not taking this seriously", "You refuse to listen", "You keep making the same mistakes", "You're being difficult for no reason", "This is why things don't work out", "You don't think before you speak", "You're making this worse", "You're acting selfish", "You ignored my advice again", "You don't learn from your mistakes", "You always avoid responsibility", "You don't respect boundaries", "You make everything dramatic", "You turned a small issue into a big problem", "You're being unfair", "You just want to argue", "You're not even paying attention", "You keep disappointing me", "You refuse to see the problem", "You don't acknowledge your mistakes", "You made this unnecessarily complicated"],
        "tone": "aggressive", "emoji": "💢", "label": "Aggressive 🔥",
        "why": "Saying such things might hurt other's feelings, try to be a little considerate while using words.",
        "rewrite": "I felt really frustrated by that and I'd like to understand your perspective.",
        "tip": "Attack the problem, never the person."
    },
    {
        "match": ["nevermind", "doesn't matter", "i just don't", "nothing"],
        "tone": "mood-out", "emoji": "🫥", "label": "Dismissive 🥶",
        "why": "Withdrawing suddenly makes the other person feel guilty without knowing why.",
        "rewrite": "I'm struggling to express this — it does matter to me, can we try again?",
        "tip": "Withdrawing without explanation breeds anxiety."
    },
    {
        "match": ["do i even matter", "don't matter to you","i feel ignored","i just don't feel like i'm important to you","do i even matter to you","i feel unwanted"],
        "tone": "Insecurity", "emoji": "🥺", "label": "Vulnerable 😓",
        "why": "This expresses real hurt but frames it as a test — it can feel manipulative even when genuine.",
        "rewrite": "I've been feeling disconnected from you lately and I miss feeling close to you.",
        "tip": "State the need, not the fear."
    },
    {
        "match": ["shut up","screw you","i hate you"],
        "tone": "aggressive", "emoji": "🤬", "label": "Aggressive 🔥",
        "why": " Such statements silence someone directly — it's a command, not a conversation.",
        "rewrite": "I'm feeling overwhelmed and need a minute before we continue.",
        "tip": "Ask for space."
    },
    {
        "match": ["hate"],
        "tone": "aggressive", "emoji": "🔥", "label": "Aggressive 🔥",
        "why": "'Hate' signals total rejection — it's extreme and hard to walk back.",
        "rewrite": "I'm really struggling with this and feeling a lot of frustration right now.",
        "tip": "'Hate' closes doors. Try 'frustrated' instead."
    },
    {
        "match": ["worthless", "useless"],
        "tone": "aggressive", "emoji": "💢", "label": "Aggressive 🔥",
        "why": "Labelling someone as worthless or useless is a direct attack on their identity.",
        "rewrite": "I felt unsupported in that moment. Can we talk about what happened?",
        "tip": "Describe the impact, not the person."
    },
    {
        "match": ["like","love", "misery", "sucks", "garbage", "trash", "horrible", "awful", "dumb", "screw you"],
        "tone": "aggressive", "emoji": "💢", "label": "Aggressive 🔥",
        "why": "Labelling someone as worthless or useless is a direct attack on their identity, you can try to be a little empathetic instead.",
        "rewrite": "I heard that you're having a hard time, do you want to talk about it?",
        "tip": "Empathy is important, try to understand before judging."
    },
    {
        "match": ["love","darling","honey","sweetheart","you're my everything", "i love you"],   
        "tone": "cheesy", "emoji": "🫣", "label": "Cheesy 🙈",
        "why": "Overly affectionate language can feel manipulative or insincere.",
        "rewrite": "I care about you and want to make sure we're both comfortable with how we communicate.",
        "tip": "Be genuine in your expressions of care."
    },
     {
        "match": ["what","why","how","when","where", "for what"],   
        "tone": "Questioning", "emoji": "🫣", "label": "Confused 🤔",
        "why": "Asking too many questions without context can be overwhelming.",
        "rewrite": "I'm not sure what you're referring to — can you clarify?",
        "tip": "Be specific in your questions."
    },
]

FALLBACK = {
    "tone": "neutral", "emoji": "🤔", "label": "Neutral ✅",
    "why": "This message has a neutral surface tone, but context and delivery still matter.",
    "rewrite": "I want to make sure we're on the same page — can we talk about how this landed?",
    "tip": "Tone in text is easy to misread — add warmth."
}


def analyze_message(message):
    lower = message.lower()

    # Find flagged words
    aggressive_found = [w for w in AGGRESSIVE_WORDS if w in lower]
    passive_found    = [w for w in PASSIVE_WORDS    if w in lower]

    # Match a rule
    matched = None
    for rule in RULES:
        if any(kw in lower for kw in rule["match"]):
            matched = rule
            break

    if matched:
        result = {
            "tone":     matched["tone"],
            "emoji":    matched["emoji"],
            "label":    matched["label"],
            "why":      matched["why"],
            "rewrite":  matched["rewrite"],
            "tip":      matched["tip"],
        }
    else:
        base_tone = "aggressive" if aggressive_found else "passive" if passive_found else "neutral"
        result = {**FALLBACK, "tone": base_tone}

    result["aggressive_words"] = aggressive_found
    result["passive_words"]    = passive_found
    result["original"]         = message
    return result


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/analyze", methods=["POST"])
def analyze():
    body    = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    return jsonify(analyze_message(message))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("✅ Conversation Rewind backend running on http://localhost:5000")
    app.run(debug=True, port=5000)