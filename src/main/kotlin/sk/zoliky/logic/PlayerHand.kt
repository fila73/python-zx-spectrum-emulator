package sk.zoliky.logic

import sk.zoliky.model.Card
import sk.zoliky.model.Rank
import sk.zoliky.model.Suit

/**
 * Manages the cards held by a player.
 */
class PlayerHand {
    private val _cards = mutableListOf<Card>()
    
    // Inject validator for game rules
    private val validator = CombinationValidator()

    /**
     * returns an immutable list of cards in the hand.
     */
    fun getCards(): List<Card> = _cards.toList()

    /**
     * Adds a card to the hand.
     */
    fun addCard(card: Card) {
        _cards.add(card)
    }

    /**
     * Removes a card from the hand.
     * @return true if the card was removed, false if it wasn't in the hand.
     */
    fun removeCard(card: Card): Boolean {
        return _cards.remove(card)
    }

    /**
     * Sorts the cards in the hand.
     * @param bySuit if true, sorts by Suit then Rank. If false, sorts by Rank then Suit.
     */
    fun sortCards(bySuit: Boolean = true) {
        if (bySuit) {
            _cards.sortWith(compareBy<Card> { it.suit }.thenBy { it.rank })
        } else {
            _cards.sortWith(compareBy<Card> { it.rank }.thenBy { it.suit })
        }
    }

    /**
     * Validates if the provided combinations meet the requirements for the initial meld.
     * Requirements:
     * 1. Total points of all valid combinations must be >= 42.
     * 2. At least one sequence must be "pure" (no Jokers).
     * 3. All combinations must be individually valid (Set or Sequence).
     * 
     * @param combinations list of card lists, where each list represents a candidate meld.
     * @return true if valid initial meld.
     */
    fun canMeld(combinations: List<List<Card>>): Boolean {
        var totalPoints = 0
        var hasPureSequence = false

        for (combo in combinations) {
            // Check if valid Set OR valid Sequence
            val isSet = validator.isValidSet(combo)
            val isSequence = validator.isValidSequence(combo)

            if (!isSet && !isSequence) {
                return false // Invalid combination found
            }

            // Calculate points
            totalPoints += validator.calculatePoints(combo)

            // Check for pure sequence (Sequence with no Jokers)
            if (isSequence) {
                val hasJoker = combo.any { it.isJoker() }
                if (!hasJoker) {
                    hasPureSequence = true
                }
            }
        }

        return totalPoints >= 42 && hasPureSequence
    }
}
