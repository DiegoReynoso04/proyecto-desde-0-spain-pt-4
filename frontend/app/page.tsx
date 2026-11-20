import Link from "next/link";

// Página provisional de la Fase 0. La landing real se construye en la Fase 3.
export default function Home() {
  return (
    <>
      <header className="border-b border-terracota-500">
        <nav aria-label="Principal" className="mx-auto max-w-5xl px-4 py-4">
          <Link href="/" className="text-xl font-bold">
            TallerYA
          </Link>
        </nav>
      </header>

      <main id="contenido" tabIndex={-1} className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
        <h1 className="text-3xl font-bold sm:text-4xl">TallerYA</h1>
        <p className="mt-4 text-lg">
          Talleres <strong>presenciales</strong> de cocina, cerámica, música, pintura, dibujo y
          fotografía.
        </p>
        <p className="mt-2">Estamos preparando la web. Muy pronto podrás reservar tu plaza.</p>
      </main>

      <footer className="border-t border-terracota-500">
        <p className="mx-auto max-w-5xl px-4 py-4 text-sm">
          © TallerYA · Todos los cursos son presenciales.
        </p>
      </footer>
    </>
  );
}
