'use server';

import { Box, Button, Container, Heading, Section, Separator, Text } from '@radix-ui/themes';
import { cookies } from 'next/headers';
import Link from 'next/link';
import { redirect } from 'next/navigation';

export default async function Home() {
  const cookieStore = await cookies();
  const isLoggedIn = !!cookieStore.get('token');

  if (isLoggedIn) {
    redirect('/dashboard');
  }

  return (
    <Box className="flex min-h-screen flex-col">
      <Section>
        <Container>
          <header className="bg-background sticky top-0 z-40 w-full border-b">
            <div className="container flex h-16 items-center justify-between py-4">
              <div className="flex items-center gap-2">
                <Heading size="6" as="h1">
                  OrchestrAI <Separator /> Los Angeles, CA
                </Heading>
              </div>
              <div className="flex items-center gap-2">
                <Link href="/login">
                  <Button title="Login">Login</Button>
                </Link>
                <Link href="/register">
                  <Button title="Sign Up">Sign Up</Button>
                </Link>
              </div>
            </div>
          </header>
        </Container>
      </Section>

      <Container>
        <main className="flex-1">
          <Section className="w-full py-12 md:py-24 lg:py-32">
            <div className="container flex flex-col items-center justify-center gap-4 px-4 text-center md:px-6">
              <div className="space-y-3">
                <Heading size="6" as="h1">
                  Chat with Your Documentation
                </Heading>
                <Text className="mx-auto max-w-[700px] text-gray-500 dark:text-gray-400 md:text-xl">
                  Create custom chat agents by simply providing a URL to your documentation. Get
                  contextually relevant answers in seconds.
                </Text>
              </div>
              <div className="flex flex-col gap-2 min-[400px]:flex-row">
                <Link href="/register">
                  <Button title="Get Started">Get Started</Button>
                </Link>
                <Link href="/how-it-works">
                  <Button title="Learn More" variant="outline">
                    Learn More
                  </Button>
                </Link>
              </div>
            </div>
          </Section>
          <Section className="bg-muted w-full py-12 md:py-24 lg:py-32">
            <div className="container grid items-center gap-6 px-4 md:px-6 lg:grid-cols-2 lg:gap-10">
              <div className="space-y-4">
                <Heading size="6" as="h2">
                  How It Works
                </Heading>
                <Text className="text-gray-500 dark:text-gray-400 md:text-xl">
                  OrchestrAI uses Retrieval Augmented Generation (RAG) to chat with your
                  documentation. Simply provide a URL, and our system crawls and processes the
                  content, making it instantly available for querying.
                </Text>
              </div>
              <div className="bg-background flex flex-col gap-2 rounded-lg border p-4 md:p-6">
                <div className="flex items-center gap-2">
                  <div className="bg-primary flex h-8 w-8 items-center justify-center rounded-full text-white">
                    1
                  </div>
                  <Heading size="6" as="h3">
                    Upload Documentation
                  </Heading>
                </div>
                <Text className="text-sm text-gray-500 dark:text-gray-400">
                  Provide a URL or upload documentation files.
                </Text>
                <div className="flex items-center gap-2">
                  <div className="bg-primary flex h-8 w-8 items-center justify-center rounded-full text-white">
                    2
                  </div>
                  <Heading size="6" as="h3">
                    Create Agent
                  </Heading>
                </div>
                <Text className="text-sm text-gray-500 dark:text-gray-400">
                  Customize your chat agent with a name and description.
                </Text>
                <div className="flex items-center gap-2">
                  <div className="bg-primary flex h-8 w-8 items-center justify-center rounded-full text-white">
                    3
                  </div>
                  <Heading size="6" as="h3">
                    Start Chatting
                  </Heading>
                </div>
                <Text className="text-sm text-gray-500 dark:text-gray-400">
                  Ask questions in natural language and get contextually relevant answers.
                </Text>
              </div>
            </div>
          </Section>
        </main>
      </Container>
      <Section>
        <Box>
          <Container>
            <footer className="w-full border-t py-6 md:py-0">
              <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
                <Text className="text-sm text-gray-500 dark:text-gray-400">
                  &copy; {new Date().getFullYear()} OrchestrAI. All rights reserved.
                </Text>
                <div className="flex gap-4">
                  <Link href="/terms" className="text-sm text-gray-500 dark:text-gray-400">
                    Terms
                  </Link>
                  <Link href="/privacy" className="text-sm text-gray-500 dark:text-gray-400">
                    Privacy
                  </Link>
                </div>
              </div>
            </footer>
          </Container>
        </Box>
      </Section>
    </Box>
  );
}
