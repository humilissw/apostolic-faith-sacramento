import { AuthProvider } from "@/context/auth-context";
import { FeatureFlagProvider } from "@/context/feature-flag-context";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import AuthGuard from "@/components/auth-guard";

import {
  Barlow_Condensed,
  EB_Garamond,
  Libre_Baskerville,
  Lora,
  Merriweather,
  Noto_Serif,
  Playfair_Display,
  PT_Serif,
  Roboto,
  Noto_Sans,
  Work_Sans,
  Epilogue,
} from "next/font/google";

const roboto = Roboto({
  weight: ["100", "300", "400", "500", "700", "900"],
  variable: "--font-roboto",
  preload: false,
});
const noto_sans = Noto_Sans({
  weight: ["100", "300", "400", "500", "700", "900"],
  variable: "--font-noto_sans",
  preload: false,
});
const work_sans = Work_Sans({
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-work_sans",
  preload: false,
});
const epilogue = Epilogue({
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-epilogue",
  preload: false,
});
const playfair = Playfair_Display({
  variable: "--font-playfair",
  preload: false,
});
const lora = Lora({
  weight: ["400", "500", "600", "700"],
  variable: "--font-lora",
  preload: false,
});
const libre = Libre_Baskerville({
  weight: ["400", "700"],
  variable: "--font-libre",
  preload: false,
});
const merriweather = Merriweather({
  variable: "--font-merriweather",
  preload: false,
});
const noto = Noto_Serif({ variable: "--font-noto", preload: false });
const pt = PT_Serif({
  weight: ["400", "700"],
  variable: "--font-pt",
  preload: false,
});
const eb = EB_Garamond({ variable: "--font-gara", preload: false });
const barlow_condensed = Barlow_Condensed({
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-barlow_condensed",
  preload: false,
});

export default function MediaLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider>
      <FeatureFlagProvider>
        <div
          className={
            `${playfair.variable} ${lora.variable} ${libre.variable} ${merriweather.variable} ` +
            `${noto.variable} ${pt.variable} ${eb.variable} ${barlow_condensed.variable} ` +
            `${roboto.variable} ${noto_sans.variable} ${work_sans.variable} ${epilogue.variable}`
          }
        >
          <Navbar />
          <main className="flex-1">
            <AuthGuard>{children}</AuthGuard>
          </main>
          <Footer />
        </div>
      </FeatureFlagProvider>
    </AuthProvider>
  );
}
