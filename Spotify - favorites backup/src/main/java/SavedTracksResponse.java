import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class SavedTracksResponse {
    public List<Item> items;
    public int total;

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Item {
        public Track track;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Track {
        public String name;
        public List<Artist> artists;
        public Album album;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Album {
        public String name;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Artist {
        public String name;
    }

}