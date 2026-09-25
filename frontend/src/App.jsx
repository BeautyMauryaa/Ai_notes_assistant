import React, { useEffect, useState } from "react";
import { fetchNotes, createNote, login } from "./api";

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("access_token")
  );

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");

  const loadNotes = async () => {
    try {
      const data = await fetchNotes();
      setNotes(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load notes. Please login again.");
    }
  };

  useEffect(() => {
    if (!isLoggedIn) return;

    loadNotes();

    const interval = setInterval(loadNotes, 4000);

    return () => clearInterval(interval);
  }, [isLoggedIn]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await login(username, password);

      setIsLoggedIn(true);
      setUsername("");
      setPassword("");
    } catch (err) {
      console.error(err);
      setError("Invalid username or password.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await createNote(title, content);

      setTitle("");
      setContent("");

      await loadNotes();
    } catch (err) {
      console.error(err);
      setError("Failed to create note.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setIsLoggedIn(false);
    setNotes([]);
  };

  if (!isLoggedIn) {
    return (
      <div
        style={{
          maxWidth: 400,
          margin: "100px auto",
          fontFamily: "sans-serif",
        }}
      >
        <h1>AI Notes Assistant</h1>

        <h2>Login</h2>

        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{
              width: "100%",
              padding: 10,
              marginBottom: 10,
              boxSizing: "border-box",
            }}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              width: "100%",
              padding: 10,
              marginBottom: 10,
              boxSizing: "border-box",
            }}
          />

          <button type="submit">Login</button>
        </form>

        {error && (
          <p style={{ color: "red" }}>
            {error}
          </p>
        )}
      </div>
    );
  }

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "40px auto",
        fontFamily: "sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h1>AI Notes Assistant</h1>

        <button onClick={handleLogout}>Logout</button>
      </div>

      <form onSubmit={handleSubmit}>
        <input
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          style={{
            width: "100%",
            marginBottom: 8,
            boxSizing: "border-box",
          }}
        />

        <textarea
          placeholder="Write your note..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={4}
          style={{
            width: "100%",
            marginBottom: 8,
            boxSizing: "border-box",
          }}
        />

        <button type="submit">Add Note</button>
      </form>

      {error && (
        <p style={{ color: "red" }}>
          {error}
        </p>
      )}

      <hr />

      {notes.map((note) => (
        <div
          key={note.id}
          style={{
            border: "1px solid #ddd",
            padding: 12,
            marginBottom: 12,
          }}
        >
          <h3>{note.title}</h3>

          <p>{note.content}</p>

          <p>
            <strong>AI status:</strong> {note.ai_status}
          </p>

          {note.ai_summary && (
            <p>
              <strong>Summary:</strong> {note.ai_summary}
            </p>
          )}

          {note.ai_tags?.length > 0 && (
            <p>
              <strong>Tags:</strong>{" "}
              {note.ai_tags.join(", ")}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}