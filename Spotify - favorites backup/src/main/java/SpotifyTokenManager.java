import io.restassured.response.Response;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Base64;
import java.util.concurrent.locks.ReentrantLock;
import static io.restassured.RestAssured.given;

public class SpotifyTokenManager {

    private final String clientId = SpotifyConfig.get("spotify.client.id");
    private final String clientSecret = SpotifyConfig.get("spotify.client.secret");
    private final String refreshToken = SpotifyConfig.get("spotify.refresh.token");
    private final String authUrl = SpotifyConfig.get("spotify.auth.url");

    private volatile String accessToken;
    private volatile Instant expiryTime;

    private final ReentrantLock lock = new ReentrantLock();

    public String getValidAccessToken() {

        if (accessToken != null && Instant.now().isBefore(expiryTime)) {
            return accessToken;
        }

        lock.lock();
        try {
            if (accessToken == null || Instant.now().isAfter(expiryTime)) {
                refreshAccessToken();
            }
            return accessToken;
        } finally {
            lock.unlock();
        }
    }

    private void refreshAccessToken() {

        String basicAuth = Base64.getEncoder()
                .encodeToString((clientId + ":" + clientSecret)
                        .getBytes(StandardCharsets.UTF_8));

        Response response =
                given()
                        .header("Authorization", "Basic " + basicAuth)
                        .contentType("application/x-www-form-urlencoded")
                        .formParam("grant_type", "refresh_token")
                        .formParam("refresh_token", refreshToken)
                        .when()
                        .post(authUrl)
                        .then()
                        // .log().all()
                        .statusCode(200)
                        .extract()
                        .response();

        this.accessToken = response.jsonPath().getString("access_token");
        int expiresIn = response.jsonPath().getInt("expires_in");

        // buffer -30 сек
        this.expiryTime = Instant.now().plusSeconds(expiresIn - 30);
    }
}