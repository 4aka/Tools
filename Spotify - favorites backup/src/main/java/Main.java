public class Main {

    public static void main(String[] args) {

        SpotifyTokenManager tokenManager = new SpotifyTokenManager();
        SpotifyService service = new SpotifyService(tokenManager);

        service.getAllSavedTracks();
    }
}