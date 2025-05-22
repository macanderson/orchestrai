import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";
import React from "react";
import { Button } from "@/components/ui/button";

export default function Home() {
  // Check if user is logged in

  // @ts-expect-error next/headers cookies() is sync in app router
  const cookieStore = await cookies();
  const isLoggedIn = !!cookieStore.get("token");

  if (isLoggedIn) {
    redirect("/dashboard");
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 w-full border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold">DocuChat</h1>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/login">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link href="/register">
              <Button>Sign Up</Button>
            </Link>
          </div>
        </div>
      </header>
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container flex flex-col items-center justify-center gap-4 px-4 text-center md:px-6">
            <div className="space-y-3">
              <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl">
                Chat with Your Documentation
              </h1>
              <p className="mx-auto max-w-[700px] text-gray-500 dark:text-gray-400 md:text-xl">
                Create custom chat agents by simply providing a URL to your
                documentation. Get contextually relevant answers in seconds.
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Link href="/register">
                <Button className="px-8">Get Started</Button>
              </Link>
              <Link href="/how-it-works">
                <Button variant="outline" className="px-8">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </section>
        <section className="w-full py-12 md:py-24 lg:py-32 bg-muted">
          <div className="container grid items-center gap-6 px-4 md:px-6 lg:grid-cols-2 lg:gap-10">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">
                How It Works
              </h2>
              <p className="text-gray-500 dark:text-gray-400 md:text-xl">
                DocuChat uses Retrieval Augmented Generation (RAG) to chat with
                your documentation. Simply provide a URL, and our system crawls
                and processes the content, making it instantly available for
                querying.
              </p>
            </div>
            <div className="flex flex-col gap-2 rounded-lg border bg-background p-4 md:p-6">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-white">
                  1
                </div>
                <h3 className="font-semibold">Upload Documentation</h3>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Provide a URL or upload documentation files.
              </p>
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-white">
                  2
                </div>
                <h3 className="font-semibold">Create Agent</h3>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Customize your chat agent with a name and description.
              </p>
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-white">
                  3
                </div>
                <h3 className="font-semibold">Start Chatting</h3>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Ask questions in natural language and get contextually relevant
                answers.
              </p>
            </div>
          </div>
        </section>
      </main>
      <footer className="w-full border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            &copy; {new Date().getFullYear()} DocuChat. All rights reserved.
          </p>
          <div className="flex gap-4">
            <Link
              href="/terms"
              className="text-sm underline text-gray-500 dark:text-gray-400"
            >
              Terms
            </Link>
            <Link
              href="/privacy"
              className="text-sm underline text-gray-500 dark:text-gray-400"
            >
              Privacy
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
