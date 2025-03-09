declare namespace App {
  interface Locals {
    django?: {
      context: {
        [key: string]: any;
      };
    };
  }
}
