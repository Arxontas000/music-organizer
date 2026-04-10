import { useState } from "react";
import { CheckIcon } from "@heroicons/react/24/solid";

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
  const [progress, setProgress] = useState<number | null>(null);
  const [completed, setCompleted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    setProgress(0);
    setCompleted(false);
    setError(null);

    if (!path) {
      setError("Please enter a path first.");
      return;
    }

    setLoading(true);
    setData(null);

    try {
      // 1. Start scan
      const res = await fetch(
        `${API_BASE}/scan/?path=${encodeURIComponent(path)}`,
      );
      const json = await res.json();

      const taskId = json.task_id;

      if (!taskId) {
        setError(json.error || "Failed to start scan.");
        setLoading(false);
        return;
      }

      // 2. Poll task status
      const poll = async () => {
        const res = await fetch(`${API_BASE}/task/${taskId}/`);
        const statusData = await res.json();

        if (statusData.status === "SUCCESS") {
          setProgress(100);
          setData(statusData.result);
          setLoading(false);
          setCompleted(true);
        } else if (statusData.status === "PROGRESS") {
          setProgress(statusData.result?.progress || 0);
          setTimeout(poll, 200);
        } else if (statusData.status === "FAILURE") {
          console.error("Task failed:", statusData);
          setError("Scan failed. Please try again.");
          setLoading(false);
        } else {
          setTimeout(poll, 1000);
        }
      };

      poll();
    } catch (err) {
      console.error("Scan error:", err);
      setError("Something went wrong while scanning.");
      setLoading(false);
    }
  };

  const handlePreview = async () => {
    if (!path) {
      setError("Please enter a path first.");
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
          disabled={loading}
          className={`w-full p-2 border rounded mb-4 ${
            loading ? "bg-gray-200 cursor-not-allowed" : ""
          }`}
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

          {completed && !loading && (
            <div className="flex items-center gap-1 text-green-600 font-semibold ml-2">
              <CheckIcon className="w-5 h-5" />
              <span>Completed</span>
            </div>
          )}
        </div>

        {loading && (
          <div className="mb-4">
            {progress !== null && progress > 0 && (
              <div className="relative w-full bg-gray-200 rounded h-6 overflow-hidden">
                <div
                  className={`h-6 transition-all duration-300 flex items-center justify-center text-white text-sm font-semibold ${
                    (progress || 0) > 80 ? "bg-green-500" : "bg-blue-500"
                  }`}
                  style={{ width: `${progress || 0}%` }}
                >
                  {progress}%
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
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
