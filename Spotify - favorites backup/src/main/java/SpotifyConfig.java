import java.io.InputStream;
import java.util.Properties;

public final class SpotifyConfig {

    private static final Properties PROPS = new Properties();

    static {
        try (InputStream is = SpotifyConfig.class
                .getClassLoader()
                .getResourceAsStream("spotify.properties")) {

            if (is == null) {
                throw new IllegalStateException("spotify.properties not found");
            }
            PROPS.load(is);

        } catch (Exception e) {
            throw new RuntimeException("Failed to load spotify.properties", e);
        }
    }

    public static String get(String key) {
        return PROPS.getProperty(key);
    }
}