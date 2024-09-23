import random

beastars_quotes = [
    ("Legoshi", "I don't know if it's because I'm a carnivore, but I feel like I'm always suppressing myself."),
    ("Haru", "I'm small and weak. But I'm not helpless."),
    ("Louis", "In this world, the strong eat the weak. That's just how it is."),
    ("Juno", "I want to be strong. Strong enough to protect someone."),
    ("Jack", "Legoshi, you're my best friend. No matter what happens, that won't change."),
    ("Gouhin", "Kid, the world isn't as simple as you think it is."),
    ("Legoshi", "I don't want to hurt anyone. I want to protect."),
    ("Haru", "I'm not afraid of you, Legoshi."),
    ("Louis", "We're all actors on a stage, playing our parts."),
    ("Legoshi", "I'm more than just my instincts. I can choose who I want to be.")
]

def get_beastars_quote():
    character, quote = random.choice(beastars_quotes)
    return f'"{quote}" - {character} (BEASTARS)'

# Example usage
if __name__ == "__main__":
    print(get_beastars_quote())