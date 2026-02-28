import io.restassured.RestAssured;
import io.restassured.specification.RequestSpecification;

public class SpotifyHttpClient {

    private final SpotifyTokenManager tokenManager;
    private final RequestSpecification baseSpec;

    public SpotifyHttpClient(SpotifyTokenManager tokenManager) {

        this.tokenManager = tokenManager;

        RestAssured.baseURI = SpotifyConfig.get("spotify.api.base.url");

        this.baseSpec = RestAssured
                .given()
                .header("Content-Type", "application/json");
    }

    public RequestSpecification authorizedRequest() {
        return baseSpec
                .header("Authorization", "Bearer " + tokenManager.getValidAccessToken());
    }
}