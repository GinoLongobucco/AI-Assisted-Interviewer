import "@/styles/globals.css";

export const metadata = {
  title: "Ai Assisted Interviewer",
  description: "Proyecto final de ANYONE",
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}

