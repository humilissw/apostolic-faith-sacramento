import Link from "next/link";

export default function NotFound() {
  return (
    <div className={`flex items-center justify-center h-screen flex-col`}>
      <h2 className="text-2xl">Not Found</h2>
      <hr/>
      <p>Could not find requested resource</p>
      <hr />
      <Link href="/">Return Home</Link>
    </div>
  );
}
