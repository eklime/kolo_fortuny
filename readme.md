# Koło Fortuny (Wheel of Fortune)

A Polish version of the classic Wheel of Fortune game implemented in Python using Tkinter.

## Game Description

Koło Fortuny is a word-guessing game where players spin a wheel to determine potential points, then guess letters to reveal a hidden phrase. The objective is to solve the phrase and accumulate the most points across multiple rounds.

## Features

- Support for multiple players (2 or more)
- Multiple rounds of gameplay
- Custom phrase lists via JSON import
- Categories for phrases
- Detailed statistics tracking
- Vowel purchases (for 200 points)
- Special wheel segments (BANKRUCTWO/Bankruptcy, STOP)
- Full phrase guessing

## How to Play

1. **Setup**:
   - Launch the game by running `python kolo_fortuny_gui.py`
   - Enter the number of players and rounds
   - Optionally import a custom JSON file with phrases
   - Enter player names

2. **Gameplay**:
   - Players take turns spinning the wheel
   - After spinning, players can:
     - Guess a consonant (free)
     - Buy a vowel (costs 200 points)
     - Solve the entire phrase

3. **Wheel Values**:
   - Point values range from 100 to 1000
   - BANKRUCTWO (Bankruptcy): Player loses all points
   - STOP: Player loses their turn

4. **Scoring**:
   - Correct consonant: Player earns wheel value × number of occurrences
   - Vowels cost 200 points to guess
   - Solving the phrase correctly: Bonus 1000 points
   - Solving incorrectly: Player loses their turn

5. **Winning**:
   - After completing all rounds, the player with the highest total score wins

## Custom Phrase Lists

You can use your own list of phrases by creating a JSON file with the following format:

```json
[
  ["Phrase 1", "Category 1"],
  ["Phrase 2", "Category 2"],
  ...
]