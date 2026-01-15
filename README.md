# Svensk Transkrebering - Webapp

En webbaserad applikation för att transkribera svenskt tal till text med hjälp av AI (KBLab Whisper).

## Funktioner

*   **Ingen installation krävs:** Körs direkt i webbläsaren.
*   **AI-driven:** Använder KBLab:s kraftfulla Whisper-modell för svenska.
*   **Filuppladdning:** Dra och släpp ljudfiler direkt i fönstret.
*   **Flexibel anslutning:** Kan köras anonymt (gratis/kösystem) eller med din egen Hugging Face API-token för snabbare/säkrare åtkomst.
*   **Modern Design:** Premium dark-mode gränssnitt.

## Hur man använder appen

1.  Gå till mappen `Svensk transkribering`.
2.  **Kör filen `start_app.bat`** (dubbelklicka).
    *   Detta startar en lokal webbserver vilket krävs för att API anropen ska fungera (löser "Failed to fetch").
3.  Webbläsaren öppnas automatiskt.
4.  **Ladda upp fil:** Klicka på rutan eller dra in en ljudfil (.mp3, .wav, etc.).
5.  **Transkribera:** Klicka på knappen.
6.  **(Valfritt) API Token:** För bättre prestanda, klicka på inställningsikonen (kugghjulet) och ange din Hugging Face token.

## Teknisk Info

Lösningen är byggd med "Vanilla" JavaScript, HTML och CSS för att vara så lättviktig och portabel som möjligt. Den ansluter direkt till Hugging Face Inference API.

*   `index.html`: Struktur
*   `style.css`: Design
*   `app.js`: Logik och API-anrop
