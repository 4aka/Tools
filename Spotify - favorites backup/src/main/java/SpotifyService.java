import io.restassured.response.Response;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public class SpotifyService {

    private final SpotifyTokenManager tokenManager;

    public SpotifyService(SpotifyTokenManager tokenManager) {
        this.tokenManager = tokenManager;
    }

    public void getAllSavedTracks() {
        int total = getTotal();
        int limit = 20;

        for (int i = 0; i <= total; i = i + limit) {

            Response response =
                    new SpotifyHttpClient(tokenManager)
                            .authorizedRequest()
                            .queryParam("limit", limit)
                            .queryParam("offset", i)
                            .when()
                            .get("/me/tracks")
                            .then()
                            .log().all()
                            .statusCode(200)
                            .extract()
                            .response();

            SavedTracksResponse dto = response.as(SavedTracksResponse.class);

            dto.items.forEach(item -> {
                Map<String, String> mapEntry = new HashMap<>();
                mapEntry.put("artist", item.track.artists.get(0).name);
                mapEntry.put("track", item.track.name);
                mapEntry.put("album", item.track.album.name);

                appendToFile(mapEntry, "map_tracks.txt");

                String entry = item.track.artists.get(0).name +
                        " - " + item.track.name +
                        " album - " + item.track.album.name;

                appendToFile(entry, "string_tracks.txt");
            });
        }
    }

    private void appendToFile(Map<String, String> entry, String fileName) {

        Path path = Path.of(fileName);

        StringBuilder block = new StringBuilder();

        entry.forEach((key, value) ->
                block.append(key)
                        .append("=")
                        .append(value)
                        .append(System.lineSeparator())
        );

        block.append(System.lineSeparator());

        try {
            Files.writeString(
                    path,
                    block.toString(),
                    StandardOpenOption.CREATE,
                    StandardOpenOption.APPEND
            );
        } catch (IOException e) {
            throw new RuntimeException("Failed to write tracks to file", e);
        }
    }

    private void appendToFile(String lines, String fileName) {
        Path path = Path.of(fileName);
        try {
            Files.write( path, Collections.singletonList(lines),
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND );
        } catch (IOException e) {
            throw new RuntimeException("Failed to write tracks to file", e); }
    }

    private int getTotal() {
        return new SpotifyHttpClient(tokenManager).authorizedRequest()
                .queryParam("limit", 1)
                .queryParam("offset", 0)
                .when()
                .get("/me/tracks")
                .then()
                .log().body()
                .statusCode(200)
                .extract()
                .response()
                .getBody().as(SavedTracksResponse.class)
                .total;
    }
}