import os
from openai import OpenAI

# Usar API original do OpenAI para TTS (base_url padrão)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"
)

roteiros = {
    "roteiro_01": """How many great songs stay unreleased…
just because launching feels too complicated?

I'm an artist, just like you.
And for a long time, I also thought releasing music was expensive and bureaucratic.
Until I discovered The Anchor Records.

Today, my music can be released and monetized on more than 50 platforms worldwide,
with a professional standard from the beginning.

The artist keeps 90% of the royalties, with clear contracts and security.

If you have a song you believe in, submit your demo.

The Anchor Records.
Release your music. Monetize your art.""",

    "roteiro_02": """The truth is simple:
talent alone is not enough in the music industry.
You need structure.

At The Anchor Records, every release goes through a complete process:
curation, technical preparation, professional mastering, and global distribution.

Your music reaches the world's main platforms with quality and positioning from the start.

All tracks are mastered and signed by Nytron,
a best-selling artist with more than 150 tracks in the Beatport Top 100.

Here, the artist keeps 90% of the royalties, with a long-term vision.

If you believe in your music, submit your demo.

The Anchor Records.
Structure creates growth.""",

    "roteiro_03": """The question isn't whether your music is good…
it's whether it's reaching the right people.

The Anchor Records was born inside electronic music culture.
Since 2015, we've produced events with artists like
Volac, Beltran, Dashdot, Fluxzone, Mandragora, and Holt 88.

We've also hosted events in three of Brazil's Top 50 clubs, according to House Mag:
Field Club, Like Music Club, and Chakra Club.

For almost a year, we were represented in Barcelona, Spain.
It was a unique and important experience for our growth,
allowing us to better understand the international scene and connect with the global electronic community.

When your music is released with us, it gains something many artists don't have: real network.

The Anchor Records.
From the dancefloor to the world.""",

    "roteiro_04": """I'm pretty sure you've seen some of our videos…
but you still haven't decided to submit your music.
Maybe you're wondering if it's really worth it.

The truth is, hundreds of artists have already released with The Anchor Records.
We're a label born inside the electronic scene,
producing events since 2015,
with artists like Volac, Beltran, and Dashdot in our history,
and global releases delivered with professional standards from day one.

Here, the artist keeps 90% of the royalties,
with clear contracts and real industry structure.

If you believe in your music, this might be the opportunity you've been waiting for.
Click the link, submit your demo, and let us hear what you've created.

The Anchor Records.
Your music deserves to go further."""
}

output_dir = "/home/ubuntu/video-anchor/assets/vozes"
os.makedirs(output_dir, exist_ok=True)

for nome, texto in roteiros.items():
    print(f"Gerando voz para {nome}...")
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        input=texto,
        speed=0.95
    )
    output_path = f"{output_dir}/{nome}_voz.mp3"
    response.stream_to_file(output_path)
    print(f"  Salvo em: {output_path}")

print("\nTodas as vozes geradas com sucesso!")
