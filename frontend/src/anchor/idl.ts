/**
 * Program IDL for TruChain
 * Auto-generated type definitions for the Solana program
 */

export type Truchain = {
  address: 'FGkp4CpRBNDQz2h5idbhbX7cHkbggpsUsF7enLiQE2nT';
  metadata: {
    name: 'truchain';
    version: '0.1.0';
    spec: '0.1.0';
    description: 'Created with Anchor';
  };
  instructions: [
    {
      name: 'endorseVideo';
      discriminator: [173, 7, 10, 6, 190, 162, 178, 18];
      accounts: [
        {
          name: 'official';
        },
        {
          name: 'video';
          writable: true;
        },
        {
          name: 'endorser';
          writable: true;
          signer: true;
        }
      ];
      args: [
        {
          name: 'isAuthentic';
          type: 'bool';
        }
      ];
    },
    {
      name: 'registerOfficial';
      discriminator: [236, 127, 211, 47, 78, 152, 17, 216];
      accounts: [
        {
          name: 'official';
          writable: true;
          pda: {
            seeds: [
              {
                kind: 'const';
                value: [111, 102, 102, 105, 99, 105, 97, 108];
              },
              {
                kind: 'arg';
                path: 'officialId';
              }
            ];
          };
        },
        {
          name: 'admin';
          writable: true;
          signer: true;
        },
        {
          name: 'systemProgram';
          address: '11111111111111111111111111111111';
        }
      ];
      args: [
        {
          name: 'officialId';
          type: 'u64';
        },
        {
          name: 'name';
          type: 'string';
        },
        {
          name: 'authority';
          type: 'pubkey';
        },
        {
          name: 'endorsers';
          type: {
            array: ['pubkey', 3];
          };
        }
      ];
    },
    {
      name: 'registerVideo';
      discriminator: [213, 160, 14, 162, 203, 241, 158, 196];
      accounts: [
        {
          name: 'official';
          writable: true;
        },
        {
          name: 'video';
          writable: true;
          pda: {
            seeds: [
              {
                kind: 'const';
                value: [118, 105, 100, 101, 111];
              },
              {
                kind: 'account';
                path: 'official';
              },
              {
                kind: 'arg';
                path: 'videoHash';
              }
            ];
          };
        },
        {
          name: 'authority';
          writable: true;
          signer: true;
          relations: ['official'];
        },
        {
          name: 'systemProgram';
          address: '11111111111111111111111111111111';
        }
      ];
      args: [
        {
          name: 'videoHash';
          type: {
            array: ['u8', 32];
          };
        },
        {
          name: 'ipfsCid';
          type: 'string';
        }
      ];
    }
  ];
  accounts: [
    {
      name: 'Official';
      discriminator: [111, 189, 248, 110, 255, 197, 65, 87];
    },
    {
      name: 'Video';
      discriminator: [57, 77, 160, 7, 234, 235, 39, 112];
    }
  ];
  errors: [
    {
      code: 6000;
      name: 'UnauthorizedOfficial';
      msg: "Only the official's authority can register videos";
    },
    {
      code: 6001;
      name: 'UnauthorizedEndorser';
      msg: 'Only approved endorsers can vote on videos';
    },
    {
      code: 6002;
      name: 'AlreadyVoted';
      msg: 'This endorser has already voted on this video';
    },
    {
      code: 6003;
      name: 'TooManyVotes';
      msg: 'Maximum number of votes reached for this video';
    },
    {
      code: 6004;
      name: 'VideoAlreadyExists';
      msg: 'Video already registered for this official';
    },
    {
      code: 6005;
      name: 'InvalidOfficialName';
      msg: 'Invalid official name (must be <= 32 bytes UTF-8)';
    },
    {
      code: 6006;
      name: 'InvalidIpfsCid';
      msg: 'Invalid IPFS CID format (must be non-empty and <= 64 bytes)';
    },
    {
      code: 6007;
      name: 'InvalidEndorserCount';
      msg: 'Must provide exactly 3 endorsers';
    },
    {
      code: 6008;
      name: 'DuplicateEndorsers';
      msg: 'Duplicate endorsers not allowed - each endorser must be unique';
    },
    {
      code: 6009;
      name: 'InvalidEndorser';
      msg: 'Invalid endorser pubkey - cannot be default or system program';
    }
  ];
  types: [
    {
      name: 'Official';
      type: {
        kind: 'struct';
        fields: [
          {
            name: 'officialId';
            type: 'u64';
          },
          {
            name: 'name';
            type: {
              array: ['u8', 32];
            };
          },
          {
            name: 'authority';
            type: 'pubkey';
          },
          {
            name: 'endorsers';
            type: {
              array: ['pubkey', 3];
            };
          },
          {
            name: 'bump';
            type: 'u8';
          }
        ];
      };
    },
    {
      name: 'Video';
      type: {
        kind: 'struct';
        fields: [
          {
            name: 'official';
            type: 'pubkey';
          },
          {
            name: 'videoHash';
            type: {
              array: ['u8', 32];
            };
          },
          {
            name: 'ipfsCid';
            type: {
              array: ['u8', 64];
            };
          },
          {
            name: 'timestamp';
            type: 'i64';
          },
          {
            name: 'votes';
            type: {
              vec: {
                defined: {
                  name: 'Vote';
                };
              };
            };
          },
          {
            name: 'status';
            type: {
              defined: {
                name: 'VideoStatus';
              };
            };
          },
          {
            name: 'bump';
            type: 'u8';
          }
        ];
      };
    },
    {
      name: 'VideoStatus';
      repr: {
        kind: 'rust';
      };
      type: {
        kind: 'enum';
        variants: [
          {
            name: 'Unverified';
          },
          {
            name: 'Authentic';
          },
          {
            name: 'Disputed';
          }
        ];
      };
    },
    {
      name: 'Vote';
      type: {
        kind: 'struct';
        fields: [
          {
            name: 'endorser';
            type: 'pubkey';
          },
          {
            name: 'isAuthentic';
            type: 'bool';
          }
        ];
      };
    }
  ];
};

// Import the JSON IDL
import idlJson from './truchain.json';

// Export the IDL as the default export
const idl = idlJson as unknown as Truchain;
export default idl;
