package sk.zoliky.model

/**
 * Represents the rank or value of a playing card.
 * Reprezentuje hodnotu hrací karty.
 */
enum class Rank(val value: Int) {
    TWO(2),
    THREE(3),
    FOUR(4),
    FIVE(5),
    SIX(6),
    SEVEN(7),
    EIGHT(8),
    NINE(9),
    TEN(10),
    JACK(10),
    QUEEN(10),
    KING(10),
    ACE(11), // Default high value, needs special handling for low sequence / Výchozí vysoká hodnota, vyžaduje speciální zacházení pro nízkou postupku
    JOKER(0)  // Value is determined by the card it replaces / Hodnota je určena kartou, kterou nahrazuje
}
