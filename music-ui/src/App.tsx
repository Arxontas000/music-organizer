import { useState } from "react";

type Track = {
  path: string;
  artist: string;
  title: string;
  genre: string;
};

type PreviewItem = {
  from: string;
  to: string;
};

type ApiResponse =
  | { grouped: Record<string, Track[]> }
  | { preview: PreviewItem[] }
  | { error: string };

function App() {
  const [path, setPath] = useState("");
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  const handleScan = async () => {
    if (!path) {
      alert("Please enter a path first");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(
        `${API_BASE}/scan/?path=${encodeURIComponent(path)}`,
      );
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Scan error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async () => {
    if (!path) {
      alert("Please enter a path first");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(
        `${API_BASE}/preview/?path=${encodeURIComponent(path)}`,
      );
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Preview error:", err);
    } finally {
      setLoading(false);
    }
  };

  const renderScan = () => {
    if (!data || !("grouped" in data)) return null;

    const grouped = data.grouped;

    return (
      <div className="space-y-6">
        {Object.entries(grouped).map(([genre, tracks]) => (
          <div key={genre}>
            <h2 className="text-lg font-bold mb-2 text-blue-600">
              {genre} ({tracks.length})
            </h2>

            <div className="space-y-1 ml-4">
              {tracks.map((track, i) => (
                <div key={i} className="bg-gray-100 px-3 py-2 rounded text-sm">
                  <span className="font-semibold">{track.artist}</span>
                  {" - "}
                  <span>{track.title}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderPreview = () => {
    if (!data || !("preview" in data)) return null;

    return (
      <div className="space-y-2">
        {data.preview.map((item, index) => (
          <div key={index} className="bg-gray-100 p-3 rounded border">
            <div className="text-xs text-gray-500">FROM:</div>
            <div className="text-xs break-all mb-1">{item.from}</div>

            <div className="text-xs text-gray-500">TO:</div>
            <div className="text-xs break-all text-green-600">{item.to}</div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-2xl mx-auto bg-white p-6 rounded-xl shadow">
        <h1 className="text-2xl font-bold mb-4">🎵 Music Organizer</h1>

        <input
          type="text"
          placeholder="Enter folder path (e.g. C:\\Music)"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          className="w-full p-2 border rounded mb-4"
        />

        <div className="flex gap-4 mb-4">
          <button
            onClick={handleScan}
            disabled={loading}
            className={`px-4 py-2 rounded text-white ${
              loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500"
            }`}
          >
            {loading ? "Scanning..." : "Scan"}
          </button>

          <button
            onClick={handlePreview}
            disabled={loading}
            className={`px-4 py-2 rounded text-white ${
              loading ? "bg-gray-400 cursor-not-allowed" : "bg-green-500"
            }`}
          >
            {loading ? "Loading..." : "Preview"}
          </button>
        </div>

        {loading && (
          <div className="mb-4 text-blue-600 font-semibold">Processing...</div>
        )}

        {data && "error" in data ? (
          <div className="bg-red-100 text-red-700 p-3 rounded">
            {data.error}
          </div>
        ) : data && "preview" in data ? (
          renderPreview()
        ) : data && "grouped" in data ? (
          renderScan()
        ) : (
          <pre className="bg-gray-900 text-green-400 p-4 rounded text-sm overflow-auto">
            {data ? JSON.stringify(data, null, 2) : "No data yet"}
          </pre>
        )}
      </div>
    </div>
  );
}

export default App;
