# Guide Débutant - Application Android de Scanner de Documents

## Guide Complet pour Débutant Absolu

### Étape 1 : Installer Flutter sur votre ordinateur

#### Sur Windows :

1. **Télécharger Flutter**
   - Allez sur : https://docs.flutter.dev/get-started/install/windows
   - Cliquez sur le bouton de téléchargement
   - Téléchargez le fichier ZIP (environ 1 GB)

2. **Extraire Flutter**
   - Créez un dossier `C:\src\`
   - Extrayez le fichier ZIP dans ce dossier
   - Vous devriez avoir : `C:\src\flutter\`

3. **Ajouter Flutter aux variables d'environnement**
   - Appuyez sur la touche Windows
   - Tapez "variables d'environnement"
   - Cliquez sur "Modifier les variables d'environnement système"
   - Cliquez sur "Variables d'environnement"
   - Dans "Variables utilisateur", trouvez "Path"
   - Cliquez sur "Modifier"
   - Cliquez sur "Nouveau"
   - Ajoutez : `C:\src\flutter\bin`
   - Cliquez sur "OK" partout

4. **Installer Android Studio**
   - Allez sur : https://developer.android.com/studio
   - Téléchargez Android Studio
   - Installez-le (acceptez toutes les options par défaut)

5. **Configurer Android Studio**
   - Ouvrez Android Studio
   - Allez dans : File → Settings → Plugins
   - Recherchez "Flutter"
   - Cliquez sur "Install"
   - Recherchez "Dart"
   - Cliquez sur "Install"
   - Redémarrez Android Studio

#### Sur Mac :

1. **Télécharger Flutter**
   - Allez sur : https://docs.flutter.dev/get-started/install/macos
   - Téléchargez le fichier ZIP

2. **Installer Flutter**
   ```bash
   cd ~/development
   unzip ~/Downloads/flutter_macos_*.zip
   ```

3. **Ajouter au PATH**
   ```bash
   echo 'export PATH="$PATH:$HOME/development/flutter/bin"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. **Installer Xcode** (pour iOS aussi)
   - Ouvrez l'App Store
   - Recherchez "Xcode"
   - Installez-le (c'est gratuit mais très gros, ~12 GB)

5. **Installer Android Studio** (même processus que Windows)

### Étape 2 : Vérifier l'installation de Flutter

1. **Ouvrir un terminal/invite de commande**
   - Windows : Appuyez sur `Win + R`, tapez `cmd`, appuyez sur Entrée
   - Mac : Appuyez sur `Cmd + Espace`, tapez "Terminal"

2. **Vérifier Flutter**
   ```bash
   flutter doctor
   ```

3. **Lire les résultats**
   - Des coches vertes ✓ = tout est bon
   - Des croix rouges ✗ = il faut installer quelque chose
   - Suivez les instructions affichées pour corriger les problèmes

### Étape 3 : Préparer votre téléphone Android

#### Option A : Utiliser votre téléphone physique (RECOMMANDÉ)

1. **Activer le mode développeur**
   - Ouvrez les Paramètres de votre téléphone
   - Allez dans "À propos du téléphone"
   - Trouvez "Numéro de build" ou "Version de build"
   - Tapez 7 fois sur ce numéro
   - Un message apparaîtra : "Vous êtes maintenant développeur !"

2. **Activer le débogage USB**
   - Retournez dans les Paramètres
   - Cherchez "Options pour les développeurs" (peut être sous "Système")
   - Activez "Options pour les développeurs"
   - Activez "Débogage USB"
   - Activez "Installer via USB" (si disponible)

3. **Connecter votre téléphone**
   - Branchez votre téléphone à l'ordinateur avec un câble USB
   - Sur votre téléphone, une fenêtre apparaîtra
   - Cochez "Toujours autoriser depuis cet ordinateur"
   - Appuyez sur "OK" ou "Autoriser"

4. **Vérifier la connexion**
   ```bash
   flutter devices
   ```
   - Vous devriez voir votre téléphone dans la liste

#### Option B : Utiliser un émulateur (si pas de téléphone)

1. **Ouvrir Android Studio**
2. **Créer un émulateur**
   - Cliquez sur les 3 points verticaux en haut à droite
   - Sélectionnez "Virtual Device Manager"
   - Cliquez sur "Create Device"
   - Choisissez "Pixel 5" ou "Pixel 6"
   - Cliquez sur "Next"
   - Sélectionnez "R" (API Level 30) et téléchargez-le
   - Cliquez sur "Next" puis "Finish"

3. **Démarrer l'émulateur**
   - Dans Virtual Device Manager
   - Cliquez sur le bouton "Play" ▶️ à côté de votre émulateur
   - Attendez que l'émulateur démarre (peut prendre 1-2 minutes)

### Étape 4 : Ouvrir le projet dans Android Studio

1. **Ouvrir Android Studio**
2. **Ouvrir le projet**
   - Cliquez sur "Open"
   - Naviguez vers le dossier où vous avez cloné le projet
   - Sélectionnez le dossier `mobile_app`
   - Cliquez sur "OK"

3. **Attendre l'indexation**
   - En bas de l'écran, vous verrez "Indexing..."
   - Attendez que ce soit terminé (peut prendre quelques minutes la première fois)

### Étape 5 : Installer les dépendances

1. **Ouvrir le terminal dans Android Studio**
   - En bas de l'écran, cliquez sur "Terminal"

2. **Installer les packages**
   ```bash
   flutter pub get
   ```
   - Attendez que tout se télécharge et s'installe

### Étape 6 : Lancer l'application

#### Méthode 1 : Via Android Studio (FACILE)

1. **Sélectionner votre appareil**
   - En haut de l'écran, vous verrez une liste déroulante
   - Sélectionnez votre téléphone ou émulateur

2. **Lancer l'application**
   - Cliquez sur le bouton "Play" vert ▶️ (Run)
   - OU appuyez sur `Shift + F10` (Windows) ou `Ctrl + R` (Mac)

3. **Attendre la compilation**
   - La première fois prend 2-5 minutes
   - Les fois suivantes seront beaucoup plus rapides

#### Méthode 2 : Via la ligne de commande

1. **Dans le terminal**
   ```bash
   cd mobile_app
   flutter run
   ```

### Étape 7 : Utiliser l'application

Une fois l'application lancée sur votre téléphone :

1. **Écran d'accueil**
   - Vous verrez "Document Scanner"
   - Un bouton violet "Scan Document"

2. **Autoriser la caméra**
   - Appuyez sur "Scan Document"
   - L'app demandera la permission d'utiliser la caméra
   - Appuyez sur "Autoriser" ou "Allow"

3. **Prendre une photo**
   - Positionnez un document (papier) devant la caméra
   - **ASTUCE** : Mettez le papier blanc sur une surface foncée (table noire, livre sombre, etc.)
   - Vous verrez un cadre blanc qui indique où placer le document
   - Appuyez sur le grand cercle blanc en bas pour capturer

4. **Voir et modifier**
   - L'app va automatiquement détecter les bords du document
   - Vous verrez deux versions : Original et Traité
   - Appuyez sur "Auto-Enhance" pour améliorer automatiquement la luminosité

5. **Ajuster manuellement**
   - Utilisez le curseur "Brightness" pour ajuster la luminosité
   - Utilisez le curseur "Contrast" pour ajuster le contraste
   - Activez "Black & White" pour un scan en noir et blanc (idéal pour du texte)

6. **Sauvegarder**
   - Appuyez sur le bouton "Save" (disquette verte)
   - Le document sera sauvegardé dans votre téléphone
   - Vous pouvez le partager en appuyant sur "Share" dans la notification

### Étape 8 : Créer un fichier APK (pour installer sur d'autres téléphones)

Si vous voulez installer l'app sur un autre téléphone sans ordinateur :

1. **Créer l'APK**
   ```bash
   cd mobile_app
   flutter build apk --release
   ```

2. **Trouver l'APK**
   - L'APK sera créé dans : `mobile_app/build/app/outputs/flutter-apk/app-release.apk`
   - Copiez ce fichier sur votre téléphone
   - Ouvrez-le pour l'installer

3. **Installer sur un autre téléphone**
   - Transférez le fichier APK (par email, USB, Bluetooth, etc.)
   - Sur le téléphone, activez "Sources inconnues" dans Paramètres → Sécurité
   - Ouvrez le fichier APK
   - Appuyez sur "Installer"

## Problèmes Courants et Solutions

### "Flutter command not found"
**Solution** : Vous n'avez pas ajouté Flutter au PATH. Recommencez l'Étape 1, partie 3.

### "No devices found"
**Solution** :
- Vérifiez que le débogage USB est activé
- Débranchez et rebranchez le câble USB
- Essayez un autre câble USB
- Sur le téléphone, révoquéz les autorisations et réautorisez

### "Gradle build failed"
**Solution** :
```bash
cd mobile_app/android
./gradlew clean
cd ../..
flutter clean
flutter pub get
flutter run
```

### L'application ne détecte pas bien le document
**Solution** :
- Utilisez un fond très contrasté (papier blanc sur table noire)
- Assurez-vous d'avoir un bon éclairage
- Gardez tout le document dans le cadre
- Le document doit être bien à plat

### L'application crash au démarrage
**Solution** :
- Vérifiez que votre téléphone est Android 5.0 (API 21) ou plus récent
- Réinstallez l'application
- Vérifiez les permissions dans Paramètres → Applications → Document Scanner

### La caméra ne s'ouvre pas
**Solution** :
- Vérifiez que vous avez autorisé la permission caméra
- Allez dans Paramètres → Applications → Document Scanner → Permissions
- Activez "Caméra"

## Astuces pour de Meilleurs Scans

1. **Éclairage**
   - Utilisez la lumière naturelle du jour
   - Évitez les ombres sur le document
   - Utilisez le flash de l'app si nécessaire

2. **Positionnement**
   - Tenez le téléphone bien parallèle au document
   - Gardez une distance d'environ 30-40 cm
   - Tout le document doit être visible

3. **Contraste**
   - Papier blanc → surface foncée
   - Papier coloré → surface blanche
   - Plus le contraste est fort, meilleure est la détection

4. **Types de documents**
   - Documents texte : Utilisez le mode Noir & Blanc
   - Photos/images : Utilisez la couleur avec Auto-Enhance
   - Documents anciens : Augmentez le contraste

## Vidéos Tutoriels Recommandées

Pour installer Flutter :
- YouTube : Recherchez "Flutter installation tutorial Windows 2024"
- YouTube : Recherchez "Flutter installation tutorial Mac 2024"

Pour utiliser Android Studio :
- YouTube : Recherchez "Android Studio tutorial for beginners"

## Support

Si vous avez des questions :
1. Vérifiez d'abord la section "Problèmes Courants"
2. Consultez la documentation Flutter : https://docs.flutter.dev
3. Demandez de l'aide sur Stack Overflow avec le tag [flutter]

Bon scan ! 📄✨
