    export default function RegisterPage() {
    return (
        <main>
            <div className="bg-p-8 rounded-lg shadow-lg max-w-md mx-auto">
                <h1 className="text-2xl">Login</h1>
                <form className="bg-gray-100 p-6 rounded shadow-md 
                    [&>input]:bg-white [&>input]:border [&>input]:p-2 
                    [&>input]:mb-4 [&>input]:w-full [&>button]:bg-blue-500 
                    [&>button]:text-white [&>button]:p-2 [&>button]:w-full 
                    [&>button]:rounded hover:[&>button]:bg-blue-600">
                    <input type="text" placeholder="Nombre" />
                    <input type="email" placeholder="Email" />
                    <input type="password" placeholder="Password" />
                    <button type="submit">Registrar cuenta</button>
                </form>
            </div>
        </main>
    );
}
